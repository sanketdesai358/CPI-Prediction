from __future__ import annotations

from datetime import date
import io
from pathlib import Path

import pandas as pd
import requests

from cpi_excel.constants import BASE_URLS
from cpi_excel.data import fetch_series_data, latest_common_months, records_to_wide
from cpi_excel.labstat import load_items, read_registry
from cpi_excel.math import one_month_contribution, price_updated_relative_importance
from cpi_excel.ri import load_current_relative_importance
from cpi_excel.sources import request_headers


MAJOR_GROUPS = ["SAF", "SAH", "SAA", "SAT", "SAM", "SAR", "SAE", "SAG"]


def _value_at(wide: pd.DataFrame, series_id: str, month: pd.Timestamp) -> float:
    value = wide.loc[wide["ref_month"] == month, series_id].iloc[0]
    return float(value)


def _latest_data():
    registry = read_registry(Path("registry.json"))
    codes = {"SA0", *MAJOR_GROUPS}
    entries = [entry for entry in registry if entry["item_code"] in codes]
    series = sorted(
        {
            series_id
            for entry in entries
            for series_id in (entry.get("series_nsa"), entry.get("series_sa"))
            if series_id
        }
    )
    current_year = date.today().year
    records = fetch_series_data(series, current_year - 2, current_year)
    nsa_series = [entry["series_nsa"] for entry in entries if entry.get("series_nsa")]
    sa_series = [entry["series_sa"] for entry in entries if entry.get("series_sa")]
    wide_nsa = records_to_wide(records[records["series_id"].isin(nsa_series)], nsa_series)
    wide_sa = records_to_wide(records[records["series_id"].isin(sa_series)], sa_series)
    months = latest_common_months(wide_nsa, wide_sa)
    return registry, wide_nsa, wide_sa, months


def test_major_group_contributions_reconcile_to_headline() -> None:
    registry, wide_nsa, wide_sa, months = _latest_data()
    latest = months[-1]
    prior = latest - pd.DateOffset(months=1)
    items = load_items()
    ri_data = load_current_relative_importance(items)
    assert ri_data.december_month is not None
    dec = pd.Timestamp(ri_data.december_month)
    all_prior_nsa = _value_at(wide_nsa, "CUUR0000SA0", prior)
    all_dec_nsa = _value_at(wide_nsa, "CUUR0000SA0", dec)

    by_code = {entry["item_code"]: entry for entry in registry}
    total = 0.0
    for code in MAJOR_GROUPS:
        entry = by_code[code]
        dec_ri = ri_data.ri_by_code[code]
        prior_ri = price_updated_relative_importance(
            dec_ri,
            _value_at(wide_nsa, entry["series_nsa"], prior),
            _value_at(wide_nsa, entry["series_nsa"], dec),
            all_prior_nsa,
            all_dec_nsa,
        )
        total += one_month_contribution(
            prior_ri,
            _value_at(wide_sa, entry["series_sa"], latest),
            _value_at(wide_sa, entry["series_sa"], prior),
        )

    headline_pp = 100.0 * (
        _value_at(wide_sa, "CUSR0000SA0", latest)
        / _value_at(wide_sa, "CUSR0000SA0", prior)
        - 1.0
    )
    assert abs(total - headline_pp) <= 0.05


def test_all_items_last_three_months_match_bls_news_release_values() -> None:
    _, wide_nsa, wide_sa, months = _latest_data()
    assert len(months) == 3

    response = requests.get(BASE_URLS["news_table_1"], headers=request_headers(), timeout=30)
    response.raise_for_status()
    table = pd.read_html(io.StringIO(response.text))[0]
    all_items = table.iloc[0]

    latest = months[-1]
    latest_nsa = _value_at(wide_nsa, "CUUR0000SA0", latest)
    latest_yoy = 100.0 * (
        latest_nsa
        / _value_at(wide_nsa, "CUUR0000SA0", latest - pd.DateOffset(months=12))
        - 1.0
    )
    sa_mm = [
        100.0
        * (
            _value_at(wide_sa, "CUSR0000SA0", month)
            / _value_at(wide_sa, "CUSR0000SA0", month - pd.DateOffset(months=1))
            - 1.0
        )
        for month in months
    ]

    assert round(latest_nsa, 3) == float(all_items.iloc[4])
    assert round(latest_yoy, 1) == float(all_items.iloc[5])
    assert [round(value, 1) for value in sa_mm] == [float(all_items.iloc[7]), float(all_items.iloc[8]), float(all_items.iloc[9])]
