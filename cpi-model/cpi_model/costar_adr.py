from __future__ import annotations

import calendar
import json
import math
import re
import time
from dataclasses import dataclass, asdict
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import numpy as np

from .data import entry_by_code
from .math import add_months, safe_mean
from .paths import ROOT


BASE_URL = "https://www.costar.com/products/str-benchmark/resources/press-releases"
CACHE_DIR = ROOT / "data" / "feeds" / "costar_adr"
RAW_DIR = CACHE_DIR / "raw"
PARSED_PATH = CACHE_DIR / "parsed_releases.json"
MODEL_PATH = CACHE_DIR / "model.json"
USER_AGENT = "cpi-component-dashboard/0.3 (+local research; contact: sanketsdesai.1995@gmail.com)"
MONTHS = {name.lower(): index for index, name in enumerate(calendar.month_name) if name}


@dataclass(frozen=True)
class ADRRelease:
    cadence: str
    title: str
    url: str
    publication_date: str
    adr: float
    occupancy: float | None
    revpar: float | None
    month: str | None = None
    week_start: str | None = None
    week_end: str | None = None


def _date(value: str) -> date:
    return date.fromisoformat(value)


def _month(value: date) -> str:
    return value.strftime("%Y-%m")


def _parse_named_date(day: str, month: str, year: str) -> date:
    return date(int(year), MONTHS[month.lower()], int(day))


def _metric(text: str, label: str, *, dollars: bool) -> float | None:
    money = r"(?:US\$|\$)\s*" if dollars else ""
    pattern = rf"{label}\s*:\s*{money}([0-9][0-9,]*(?:\.[0-9]+)?)\s*%?"
    match = re.search(pattern, text, re.IGNORECASE)
    return float(match.group(1).replace(",", "")) if match else None


def parse_release_text(text: str, *, title: str, url: str) -> ADRRelease | None:
    normalized = text.replace("\u00a0", " ")
    publication = re.search(r"(?:^|\n)\s*(\d{1,2})\s+([A-Za-z]+)\s+(20\d{2})\s*(?:\n|\|)", normalized)
    if not publication:
        return None
    publication_date = _parse_named_date(*publication.groups())
    adr = _metric(normalized, r"(?:Average daily rate \(ADR\)|ADR)", dollars=True)
    occupancy = _metric(normalized, r"Occupancy", dollars=False)
    revpar = _metric(normalized, r"(?:Revenue per available room \(RevPAR\)|RevPAR)", dollars=True)
    if adr is None:
        return None

    month_match = re.search(r"U\.S\. hotel performance for\s+([A-Za-z]+)\s+(20\d{2})", title, re.IGNORECASE)
    if month_match:
        month = f"{int(month_match.group(2)):04d}-{MONTHS[month_match.group(1).lower()]:02d}"
        return ADRRelease("monthly", title, url, publication_date.isoformat(), adr, occupancy, revpar, month=month)

    range_match = re.search(
        r"(\d{1,2})\s*[-–]\s*(\d{1,2})\s+([A-Za-z]+)\s+(20\d{2})",
        normalized,
        re.IGNORECASE,
    )
    if range_match:
        start = _parse_named_date(range_match.group(1), range_match.group(3), range_match.group(4))
        end = _parse_named_date(range_match.group(2), range_match.group(3), range_match.group(4))
    else:
        range_match = re.search(
            r"(\d{1,2})\s+([A-Za-z]+)\s+(?:through|to|[-–])\s*(\d{1,2})\s+([A-Za-z]+)\s+(20\d{2})",
            normalized,
            re.IGNORECASE,
        )
        if not range_match:
            return None
        start = _parse_named_date(range_match.group(1), range_match.group(2), range_match.group(5))
        end = _parse_named_date(range_match.group(3), range_match.group(4), range_match.group(5))
        if start > end:
            start = date(end.year - 1, start.month, start.day)
    return ADRRelease(
        "weekly",
        title,
        url,
        publication_date.isoformat(),
        adr,
        occupancy,
        revpar,
        week_start=start.isoformat(),
        week_end=end.isoformat(),
    )


def parse_cached_releases() -> list[ADRRelease]:
    manifest_path = RAW_DIR / "release_manifest.json"
    if not manifest_path.exists():
        return []
    releases: list[ADRRelease] = []
    for item in json.loads(manifest_path.read_text(encoding="utf-8")):
        text_path = RAW_DIR / "releases" / f"{item['slug']}.txt"
        if not text_path.exists():
            continue
        parsed = parse_release_text(
            text_path.read_text(encoding="utf-8", errors="replace"),
            title=item["title"],
            url=item["url"],
        )
        if parsed:
            releases.append(parsed)
    releases.sort(key=lambda row: (row.publication_date, row.cadence, row.url))
    PARSED_PATH.parent.mkdir(parents=True, exist_ok=True)
    PARSED_PATH.write_text(json.dumps([asdict(row) for row in releases], indent=2), encoding="utf-8")
    return releases


def load_releases() -> list[ADRRelease]:
    if PARSED_PATH.exists():
        return [ADRRelease(**row) for row in json.loads(PARSED_PATH.read_text(encoding="utf-8"))]
    return parse_cached_releases()


def refresh_public_archive(*, max_pages: int = 39, delay_seconds: float = 1.0) -> dict[str, Any]:
    """Attempt a direct polite refresh. Cached browser captures remain usable on 403."""
    errors = []
    fetched = 0
    listings = RAW_DIR / "listings"
    listings.mkdir(parents=True, exist_ok=True)
    for page in range(max_pages):
        url = BASE_URL + (f"?page={page}" if page else "")
        request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html"})
        try:
            html = urlopen(request, timeout=30).read().decode("utf-8", errors="replace")
            (listings / f"page_{page:02d}.html").write_text(html, encoding="utf-8")
            fetched += 1
        except (HTTPError, URLError, TimeoutError) as exc:
            errors.append(f"{url}: {type(exc).__name__} {exc}")
            break
        time.sleep(delay_seconds)
    return {"fetchedPages": fetched, "errors": errors, "cacheAvailable": (RAW_DIR / "release_manifest.json").exists()}


def official_monthly(releases: list[ADRRelease], *, as_of: date | None = None) -> dict[str, ADRRelease]:
    out = {}
    for row in releases:
        if row.cadence != "monthly" or not row.month:
            continue
        if as_of and _date(row.publication_date) > as_of:
            continue
        out[row.month] = row
    return out


def weekly_month(
    releases: list[ADRRelease],
    month: str,
    *,
    as_of: date,
    carry_forward: bool = True,
) -> dict[str, Any] | None:
    year, mon = map(int, month.split("-"))
    month_start = date(year, mon, 1)
    month_end = date(year, mon, calendar.monthrange(year, mon)[1])
    eligible = [
        row
        for row in releases
        if row.cadence == "weekly"
        and row.week_start
        and row.week_end
        and _date(row.publication_date) <= as_of
        and _date(row.week_end) >= month_start
        and _date(row.week_start) <= month_end
    ]
    daily: dict[date, ADRRelease] = {}
    for row in eligible:
        cursor = max(_date(row.week_start or ""), month_start)
        end = min(_date(row.week_end or ""), month_end)
        while cursor <= end:
            daily[cursor] = row
            cursor += timedelta(days=1)
    latest = max(eligible, key=lambda row: (row.week_end or "", row.publication_date), default=None)
    carried_days = 0
    if carry_forward and latest:
        cursor = month_start
        while cursor <= month_end:
            if cursor not in daily:
                daily[cursor] = latest
                carried_days += 1
            cursor += timedelta(days=1)
    if not daily:
        return None
    adr = safe_mean([row.adr for row in daily.values()], 0.0)
    occupancy_values = [row.occupancy for row in daily.values() if row.occupancy is not None]
    used = sorted({row.url: row for row in daily.values()}.values(), key=lambda row: row.week_end or "")
    return {
        "month": month,
        "adr": adr,
        "occupancy": safe_mean(occupancy_values, 0.0) if occupancy_values else None,
        "observedDays": len(daily) - carried_days,
        "carriedDays": carried_days,
        "asOf": as_of.isoformat(),
        "weeklyPrints": [asdict(row) for row in used],
    }


def _pct(current: float | None, prior: float | None) -> float | None:
    return None if current is None or prior in {None, 0} else float(current) / float(prior) - 1.0


def _cpi_rows(code: str = "SEHB02") -> dict[str, float]:
    entry = entry_by_code()[code]
    out = {}
    history = entry.get("history", [])
    prior = None
    for point in history:
        index = point.get("nsaIndex")
        if index is not None and prior not in {None, 0}:
            out[point["month"]] = math.log(float(index) / float(prior))
        prior = index
    return out


def _official_features(releases: list[ADRRelease]) -> dict[str, dict[str, float | None]]:
    official = official_monthly(releases)
    months = sorted(official)
    out = {}
    for month in months:
        prior = official.get(add_months(month, -1))
        row = official[month]
        out[month] = {
            "adrMm": _pct(row.adr, prior.adr if prior else None),
            "occupancyChange": None if not prior or row.occupancy is None or prior.occupancy is None else (row.occupancy - prior.occupancy) / 100.0,
            "publicationDate": row.publication_date,
        }
    return out


def _fit_xy(rows: list[tuple[list[float], float]]) -> tuple[list[float], float | None]:
    if len(rows) < 12:
        return [], None
    x = np.asarray([row[0] for row in rows], dtype=float)
    y = np.asarray([row[1] for row in rows], dtype=float)
    beta, *_ = np.linalg.lstsq(x, y, rcond=None)
    fitted = x @ beta
    ss_tot = float(((y - y.mean()) ** 2).sum())
    r2 = None if ss_tot == 0 else 1.0 - float(((y - fitted) ** 2).sum()) / ss_tot
    return beta.tolist(), r2


def _walk_forward_mae(rows: list[tuple[list[float], float]], *, minimum: int = 12) -> float | None:
    errors = []
    for index in range(minimum, len(rows)):
        beta, _ = _fit_xy(rows[:index])
        if not beta:
            continue
        prediction = sum(weight * value for weight, value in zip(beta, rows[index][0]))
        errors.append(abs(prediction - rows[index][1]))
    return safe_mean(errors, None) if errors else None


def fit_model(releases: list[ADRRelease], *, cutoff_month: str) -> dict[str, Any] | None:
    features = _official_features(releases)
    cpi = _cpi_rows()
    raw_rows = []
    for month in sorted(set(features) & set(cpi)):
        if month >= cutoff_month:
            continue
        adr0 = features[month].get("adrMm")
        adr1 = features.get(add_months(month, -1), {}).get("adrMm")
        persistence = cpi.get(add_months(month, -1))
        occ = features[month].get("occupancyChange")
        if None in {adr0, adr1, persistence}:
            continue
        raw_rows.append((float(adr0), float(adr1), float(persistence), None if occ is None else float(occ), cpi[month]))
    if len(raw_rows) < 12:
        return None

    candidates = []
    # Keep a genuine current-month channel: the ADR nowcast is the primary driver,
    # while lag 1 absorbs delayed CPI collection/pass-through.
    for lag0_weight in [index / 20.0 for index in range(5, 21)]:
        base = [([1.0, lag0_weight * row[0] + (1.0 - lag0_weight) * row[1], row[2]], row[4]) for row in raw_rows]
        beta, r2 = _fit_xy(base)
        if not beta or not (0.0 <= beta[1] <= 1.5):
            continue
        candidates.append((_walk_forward_mae(base) or 99.0, lag0_weight, beta, r2, base))
    if not candidates:
        return None
    base_mae, lag0_weight, beta, r2, base_rows = min(candidates, key=lambda row: row[0])
    occ_rows = [
        ([1.0, lag0_weight * row[0] + (1.0 - lag0_weight) * row[1], row[2], row[3]], row[4])
        for row in raw_rows
        if row[3] is not None
    ]
    occ_beta, occ_r2 = _fit_xy(occ_rows)
    occ_mae = _walk_forward_mae(occ_rows)
    use_occupancy = bool(
        occ_beta
        and 0.0 <= occ_beta[1] <= 1.5
        and occ_mae is not None
        and base_mae is not None
        and occ_mae + 0.0001 < base_mae
    )
    chosen = occ_beta if use_occupancy else beta
    return {
        "features": ["intercept", "adr_blend", "cpi_persistence"] + (["occupancy_change"] if use_occupancy else []),
        "coefficients": chosen,
        "adrBeta": chosen[1],
        "adrLagWeights": {"lag0": lag0_weight, "lag1": 1.0 - lag0_weight},
        "r2": occ_r2 if use_occupancy else r2,
        "observations": len(occ_rows if use_occupancy else base_rows),
        "walkForwardMae": occ_mae if use_occupancy else base_mae,
        "occupancyCandidateWalkForwardMae": occ_mae,
        "occupancyCandidateR2": occ_r2,
        "occupancyIncluded": use_occupancy,
    }


def _forecast_as_of(month: str) -> date:
    next_month = add_months(month, 1)
    return date(int(next_month[:4]), int(next_month[5:]), 11)


def lodging_forecast(month: str, feed: dict[str, Any], *, as_of: date | None = None) -> dict[str, Any] | None:
    releases = [ADRRelease(**row) for row in feed.get("releases", [])]
    if not releases:
        return None
    as_of = as_of or _forecast_as_of(month)
    current = weekly_month(releases, month, as_of=as_of)
    official = official_monthly(releases, as_of=as_of)
    prior = official.get(add_months(month, -1))
    prior_prior = official.get(add_months(month, -2))
    if not current or not prior or not prior_prior:
        return None
    model = fit_model(releases, cutoff_month=month)
    if not model:
        return None
    adr0 = _pct(current["adr"], prior.adr)
    adr1 = _pct(prior.adr, prior_prior.adr)
    cpi = _cpi_rows()
    persistence = cpi.get(add_months(month, -1))
    if adr0 is None or adr1 is None or persistence is None:
        return None
    lag_weights = model["adrLagWeights"]
    adr_blend = lag_weights["lag0"] * adr0 + lag_weights["lag1"] * adr1
    values = [1.0, adr_blend, persistence]
    if model["occupancyIncluded"]:
        values.append(0.0 if current.get("occupancy") is None or prior.occupancy is None else (current["occupancy"] - prior.occupancy) / 100.0)
    forecast = float(sum(beta * value for beta, value in zip(model["coefficients"], values)))
    prints = current["weeklyPrints"]
    driver = (
        f"CoStar/STR ADR primary: {month} weekly-derived ${current['adr']:.2f} vs "
        f"{add_months(month, -1)} official ${prior.adr:.2f} ({adr0 * 100:+.2f}%); "
        f"{len(prints)} weekly prints, {current['carriedDays']} carried days; pass-through {forecast * 100:+.2f}%"
    )
    return {"forecastNsaMm": forecast, "driver": driver, "model": model, "monthlyNowcast": current, "priorOfficial": asdict(prior)}


def seasonal_ar_fallback(month: str, *, code: str = "SEHB02") -> float | None:
    cpi = _cpi_rows(code)
    values = [value for hist_month, value in sorted(cpi.items()) if hist_month < month]
    if not values:
        return None
    same_month = [value for hist_month, value in sorted(cpi.items()) if hist_month < month and hist_month[-2:] == month[-2:]]
    last = values[-1]
    trailing3 = safe_mean(values[-3:], last)
    trailing6 = safe_mean(values[-6:], trailing3)
    seasonal = safe_mean(same_month, trailing6)
    return 0.45 * last + 0.25 * trailing3 + 0.20 * seasonal + 0.10 * trailing6


def revision_statistics(releases: list[ADRRelease]) -> dict[str, Any]:
    official = official_monthly(releases)
    gaps = []
    rows = []
    for month, release in sorted(official.items()):
        derived = weekly_month(releases, month, as_of=_date(release.publication_date), carry_forward=False)
        if not derived or derived["observedDays"] < 20:
            continue
        gap = derived["adr"] / release.adr - 1.0
        gaps.append(gap)
        rows.append({"month": month, "weeklyDerivedAdr": derived["adr"], "officialAdr": release.adr, "gap": gap})
    return {
        "months": len(gaps),
        "meanAbsoluteGap": safe_mean([abs(value) for value in gaps], None),
        "meanGap": safe_mean(gaps, None),
        "rows": rows,
    }


def walk_forward_backtest(releases: list[ADRRelease], *, start: str = "2022-01") -> dict[str, Any]:
    cpi = _cpi_rows()
    rows = []
    for month in sorted(cpi):
        if month < start:
            continue
        as_of = _forecast_as_of(month)
        feed = {"releases": [asdict(row) for row in releases if _date(row.publication_date) <= as_of]}
        new = lodging_forecast(month, feed, as_of=as_of)
        old = seasonal_ar_fallback(month)
        actual = cpi.get(month)
        if actual is None or old is None:
            continue
        rows.append(
            {
                "month": month,
                "asOf": as_of.isoformat(),
                "actualNsaMm": actual,
                "adrPrimaryNsaMm": new.get("forecastNsaMm") if new else None,
                "seasonalArNsaMm": old,
                "feedAvailable": new is not None,
            }
        )
    common_months = {row["month"] for row in rows if row.get("adrPrimaryNsaMm") is not None}
    def metric(key: str, *, common: bool = False) -> dict[str, Any]:
        pairs = [
            (row[key], row["actualNsaMm"])
            for row in rows
            if row.get(key) is not None and (not common or row["month"] in common_months)
        ]
        return {
            "months": len(pairs),
            "mae": safe_mean([abs(pred - actual) for pred, actual in pairs], None),
            "rmse": math.sqrt(safe_mean([(pred - actual) ** 2 for pred, actual in pairs], 0.0)) if pairs else None,
        }
    return {
        "requestedStart": start,
        "availableStart": min(common_months) if common_months else None,
        "adrPrimary": metric("adrPrimaryNsaMm"),
        "seasonalArFull": metric("seasonalArNsaMm"),
        "seasonalArCommon": metric("seasonalArNsaMm", common=True),
        "rows": rows,
    }


def feed_payload(*, attempt_refresh: bool = False) -> dict[str, Any]:
    refresh = refresh_public_archive() if attempt_refresh else {"fetchedPages": 0, "errors": [], "cacheAvailable": True}
    releases = parse_cached_releases()
    weekly = [row for row in releases if row.cadence == "weekly"]
    monthly = [row for row in releases if row.cadence == "monthly"]
    dates = [row.publication_date for row in releases]
    status = "live_cached" if weekly and monthly else "unavailable"
    error = "; ".join(refresh.get("errors") or []) or None
    return {
        "feed": "CoStar/STR U.S. hotel ADR press releases",
        "status": status,
        "lastObservationDate": max(dates) if dates else None,
        "latestValue": releases[-1].adr if releases else None,
        "unit": "U.S. dollars ADR",
        "observations": [{"date": row.publication_date, "value": row.adr, "label": f"CoStar/STR {row.cadence} ADR"} for row in releases],
        "releases": [asdict(row) for row in releases],
        "weeklyCount": len(weekly),
        "monthlyCount": len(monthly),
        "truePublicationSpan": {"start": min(dates) if dates else None, "end": max(dates) if dates else None},
        "error": error,
    }
