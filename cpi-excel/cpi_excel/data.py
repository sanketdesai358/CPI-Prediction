from __future__ import annotations

import io
import os
from collections.abc import Iterable
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd

from .constants import BASE_URLS, LABSTAT_DIR
from .sources import download_text, post_json_cached, stable_json_hash


def chunked(items: list[str], size: int) -> Iterable[list[str]]:
    for index in range(0, len(items), size):
        yield items[index : index + size]


def _period_to_month(year: str | int, period: str) -> pd.Timestamp | None:
    if not str(period).startswith("M"):
        return None
    try:
        month = int(str(period)[1:])
        if not 1 <= month <= 12:
            return None
        return pd.Timestamp(date(int(year), month, 1))
    except ValueError:
        return None


def _parse_api_response(data: dict[str, Any]) -> pd.DataFrame:
    status = data.get("status")
    if status not in {"REQUEST_SUCCEEDED", "REQUEST_NOT_PROCESSED"}:
        raise RuntimeError(f"BLS API returned status {status!r}: {data.get('message')}")
    if status == "REQUEST_NOT_PROCESSED":
        raise RuntimeError(f"BLS API request not processed: {data.get('message')}")

    records: list[dict[str, Any]] = []
    for series in data.get("Results", {}).get("series", []):
        series_id = series.get("seriesID")
        for point in series.get("data", []):
            ref_month = _period_to_month(point.get("year"), point.get("period"))
            if ref_month is None:
                continue
            value = point.get("value")
            parsed_value = None
            if value not in (None, "", "-"):
                parsed_value = float(value)
            records.append(
                {
                    "series_id": series_id,
                    "ref_month": ref_month,
                    "value": parsed_value,
                    "latest": str(point.get("latest", "")).lower() == "true",
                }
            )
    return pd.DataFrame.from_records(records)


def fetch_series_api(
    series_ids: list[str],
    start_year: int,
    end_year: int,
    *,
    force: bool = False,
) -> pd.DataFrame:
    key = os.environ.get("BLS_API_KEY")
    batch_size = 50 if key else 25
    frames: list[pd.DataFrame] = []

    for batch_index, batch in enumerate(chunked(sorted(set(series_ids)), batch_size), start=1):
        payload: dict[str, Any] = {
            "seriesid": batch,
            "startyear": str(start_year),
            "endyear": str(end_year),
        }
        if key:
            payload["registrationkey"] = key
        cache_name = f"bls_{start_year}_{end_year}_{batch_index:03d}_{stable_json_hash(payload)}"
        data = post_json_cached(
            BASE_URLS["bls_api"], payload, cache_name=cache_name, force=force, timeout=180
        )
        messages = data.get("message") or []
        if any("reduced" in str(message).lower() for message in messages) and not key:
            raise RuntimeError(
                "BLS API reduced the batch size unexpectedly; rerun with BLS_API_KEY or clear cache."
            )
        frames.append(_parse_api_response(data))

    if not frames:
        return pd.DataFrame(columns=["series_id", "ref_month", "value", "latest"])
    return pd.concat(frames, ignore_index=True)


def fetch_series_bulk_current(
    series_ids: list[str],
    start_year: int,
    end_year: int,
    *,
    force: bool = False,
) -> pd.DataFrame:
    text = download_text(
        BASE_URLS["cu_current"],
        LABSTAT_DIR / "cu.data.0.Current",
        force=force,
        timeout=300,
    )
    df = pd.read_csv(io.StringIO(text), sep="\t", dtype=str, keep_default_na=False)
    df.columns = [column.strip() for column in df.columns]
    for column in df.columns:
        df[column] = df[column].astype(str).str.strip()

    df = df[df["series_id"].isin(set(series_ids))]
    df = df[df["period"].str.startswith("M")]
    df["year_int"] = pd.to_numeric(df["year"], errors="coerce")
    df = df[(df["year_int"] >= start_year) & (df["year_int"] <= end_year)]
    df["ref_month"] = [
        _period_to_month(year, period) for year, period in zip(df["year"], df["period"])
    ]
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df[["series_id", "ref_month", "value"]].dropna(subset=["ref_month"]).copy()


def fetch_series_data(
    series_ids: list[str],
    start_year: int,
    end_year: int,
    *,
    force: bool = False,
) -> pd.DataFrame:
    try:
        return fetch_series_api(series_ids, start_year, end_year, force=force)
    except Exception as api_error:
        print(f"BLS API fetch failed; falling back to cu.data.0.Current: {api_error}")
        return fetch_series_bulk_current(
            series_ids, start_year, end_year, force=force
        )


def records_to_wide(records: pd.DataFrame, series_ids: list[str]) -> pd.DataFrame:
    if records.empty:
        return pd.DataFrame(columns=["ref_month", *series_ids])
    wide = (
        records.pivot_table(
            index="ref_month", columns="series_id", values="value", aggfunc="last"
        )
        .sort_index()
        .reset_index()
    )
    for series_id in series_ids:
        if series_id not in wide.columns:
            wide[series_id] = pd.NA
    return wide[["ref_month", *series_ids]].copy()


def latest_common_months(wide_nsa: pd.DataFrame, wide_sa: pd.DataFrame, count: int = 3) -> list[pd.Timestamp]:
    nsa_months = set(
        wide_nsa.loc[wide_nsa["CUUR0000SA0"].notna(), "ref_month"].tolist()
        if "CUUR0000SA0" in wide_nsa
        else []
    )
    sa_months = set(
        wide_sa.loc[wide_sa["CUSR0000SA0"].notna(), "ref_month"].tolist()
        if "CUSR0000SA0" in wide_sa
        else []
    )
    months = sorted(nsa_months & sa_months)
    if len(months) < count:
        raise RuntimeError("Could not resolve the latest common CPI NSA/SA reference months.")
    return list(months[-count:])


def month_display(month: pd.Timestamp) -> str:
    return month.strftime("%b %Y")


def excel_date(month: pd.Timestamp) -> date:
    return date(int(month.year), int(month.month), 1)
