from __future__ import annotations

import argparse
from collections import defaultdict
from typing import Any

from .commodity_complex import commodity_backtest_rows
from .data import entry_by_code, write_json
from .feeds import collect_feeds, monthly_average
from .math import add_months, pct_change, safe_mean
from .paths import BACKTEST_DIR


WINDOWS = {
    "A": "2000-01",
    "B": "2016-01",
    "C": "2022-01",
}


def actual_headline_series() -> list[dict[str, Any]]:
    entry = entry_by_code()["SA0"]
    rows = []
    for point in entry["history"]:
        prior = next((item for item in entry["history"] if item["month"] == add_months(point["month"], -1)), None)
        year_ago = next((item for item in entry["history"] if item["month"] == add_months(point["month"], -12)), None)
        rows.append(
            {
                "month": point["month"],
                "actualNsaMm": pct_change(point.get("nsaIndex"), prior.get("nsaIndex") if prior else None),
                "actualSaMm": point.get("saMm"),
                "actualYoy": pct_change(point.get("nsaIndex"), year_ago.get("nsaIndex") if year_ago else None),
            }
        )
    return rows


def actual_component_series(item_code: str) -> list[dict[str, Any]]:
    entry = entry_by_code()[item_code]
    rows = []
    for point in entry["history"]:
        prior = next((item for item in entry["history"] if item["month"] == add_months(point["month"], -1)), None)
        rows.append(
            {
                "month": point["month"],
                "actualNsaMm": pct_change(point.get("nsaIndex"), prior.get("nsaIndex") if prior else None),
            }
        )
    return rows


def r2(rows: list[dict[str, Any]], forecast_key: str, actual_key: str) -> float | None:
    paired = [(row[forecast_key], row[actual_key]) for row in rows if row.get(forecast_key) is not None and row.get(actual_key) is not None]
    if len(paired) < 3:
        return None
    actuals = [actual for _, actual in paired]
    mean_actual = safe_mean(actuals, 0.0)
    ss_res = sum((forecast - actual) ** 2 for forecast, actual in paired)
    ss_tot = sum((actual - mean_actual) ** 2 for actual in actuals)
    return None if ss_tot == 0 else 1.0 - ss_res / ss_tot


def gasoline_backtest_rows(start: str) -> list[dict[str, Any]]:
    feeds = collect_feeds(write_snapshots=True)
    gas = feeds.get("gasoline_regular", {})
    points = gas.get("points") or []
    rows = []
    for row in actual_component_series("SETB01"):
        month = row["month"]
        if month < start:
            continue
        current = monthly_average(points, month)
        prior = monthly_average(points, add_months(month, -1))
        forecast = None if current is None or prior in {None, 0} else current / prior - 1.0
        rows.append({**row, "forecastNsaMm": forecast})
    return rows


def forecast_from_history(series: list[dict[str, Any]], index: int, key: str) -> float | None:
    prior = series[index - 1].get(key) if index >= 1 else None
    same_month_prior = series[index - 12].get(key) if index >= 12 else None
    trailing = [series[i].get(key) for i in range(max(0, index - 6), index)]
    clean = [value for value in trailing if value is not None]
    if prior is None and same_month_prior is None and not clean:
        return None
    return 0.45 * (prior or 0.0) + 0.35 * (same_month_prior or safe_mean(clean, 0.0)) + 0.20 * safe_mean(clean, 0.0)


def benchmark_random_walk(series: list[dict[str, Any]], index: int, key: str) -> float | None:
    return series[index - 12].get(key) if index >= 12 else None


def benchmark_ar1(series: list[dict[str, Any]], index: int, key: str) -> float | None:
    return series[index - 1].get(key) if index >= 1 else None


def mae(rows: list[dict[str, Any]], forecast_key: str, actual_key: str) -> float | None:
    errors = [
        abs(row[forecast_key] - row[actual_key])
        for row in rows
        if row.get(forecast_key) is not None and row.get(actual_key) is not None
    ]
    return safe_mean(errors, None) if errors else None


def rmse(rows: list[dict[str, Any]], forecast_key: str, actual_key: str) -> float | None:
    errors = [
        (row[forecast_key] - row[actual_key]) ** 2
        for row in rows
        if row.get(forecast_key) is not None and row.get(actual_key) is not None
    ]
    if not errors:
        return None
    return safe_mean(errors, 0.0) ** 0.5


def build_window(window: str, start: str) -> dict[str, Any]:
    series = actual_headline_series()
    cache_by_code = entry_by_code()
    gas_rows = gasoline_backtest_rows(start)
    rows = []
    for index, row in enumerate(series):
        if row["month"] < start:
            continue
        forecast_nsa = forecast_from_history(series, index, "actualNsaMm")
        forecast_sa = forecast_from_history(series, index, "actualSaMm")
        seasonal_rw = benchmark_random_walk(series, index, "actualNsaMm")
        ar1 = benchmark_ar1(series, index, "actualNsaMm")
        component_rw = safe_mean([seasonal_rw, ar1], None) if seasonal_rw is not None and ar1 is not None else None
        rows.append(
            {
                **row,
                "forecastNsaMm": forecast_nsa,
                "forecastSaMm": forecast_sa,
                "benchSeasonalRw": seasonal_rw,
                "benchAr1": ar1,
                "benchComponentRw": component_rw,
                "p10": (forecast_sa - 0.0025) if forecast_sa is not None else None,
                "p90": (forecast_sa + 0.0025) if forecast_sa is not None else None,
            }
        )
    rolling = []
    for index, row in enumerate(rows):
        window_rows = rows[max(0, index - 23) : index + 1]
        rolling.append({"month": row["month"], "mae24": mae(window_rows, "forecastNsaMm", "actualNsaMm")})
    calibration_rows = [
        row
        for row in rows
        if row.get("actualSaMm") is not None and row.get("p10") is not None and row.get("p90") is not None
    ]
    coverage = safe_mean(
        [1.0 if row["p10"] <= row["actualSaMm"] <= row["p90"] else 0.0 for row in calibration_rows],
        None,
    )
    result = {
        "window": window,
        "requestedStart": start,
        "availableStart": rows[0]["month"] if rows else None,
        "availableEnd": rows[-1]["month"] if rows else None,
        "metrics": {
            "headlineNsaMae": mae(rows, "forecastNsaMm", "actualNsaMm"),
            "headlineNsaRmse": rmse(rows, "forecastNsaMm", "actualNsaMm"),
            "headlineSaMae": mae(rows, "forecastSaMm", "actualSaMm"),
            "headlineSaRmse": rmse(rows, "forecastSaMm", "actualSaMm"),
            "seasonalRwMae": mae(rows, "benchSeasonalRw", "actualNsaMm"),
            "ar1Mae": mae(rows, "benchAr1", "actualNsaMm"),
            "componentRwMae": mae(rows, "benchComponentRw", "actualNsaMm"),
            "intervalCoverage": coverage,
            "hitRateRoundedTenth": safe_mean(
                [
                    1.0 if round((row["forecastNsaMm"] or 0) * 100, 1) == round((row["actualNsaMm"] or 0) * 100, 1) else 0.0
                    for row in rows
                    if row.get("forecastNsaMm") is not None and row.get("actualNsaMm") is not None
                ],
                None,
            ),
            "gasolineNsaMae": mae(gas_rows, "forecastNsaMm", "actualNsaMm"),
            "gasolineNsaR2": r2(gas_rows, "forecastNsaMm", "actualNsaMm"),
        },
        "rolling24": rolling,
        "componentLeague": [
            {"itemCode": "SETB01", "name": "Gasoline (all types)", "mae": 0.0, "benchmarkMae": 0.0, "note": "External feed fallback not scored in seeded cache"},
            {"itemCode": "SEHA", "name": "Rent of primary residence", "mae": 0.0, "benchmarkMae": 0.0, "note": "Shelter lag kernel placeholder"},
        ],
        "commodityComplex": {
            "window": window,
            "requestedStart": start,
            "notes": "With-granular compares sub-stratum CPI history partially pooled to the commodity-complex factor against the prior composite-only mapping. Wholesale-to-AP correlation is reported as unavailable until enough local USDA cut history is archived.",
            "rows": commodity_backtest_rows(cache_by_code, start=start),
        },
        "rows": rows,
        "benchmarks": ["seasonal random walk", "AR(1) on headline", "component random walk aggregated"],
        "diagnostics": {
            "januaryWeightPivot": "reported through month rows; archived RI vintages are a configured future extension",
            "februarySeasonalFactorSwap": "SA offsets are derived from published SA/NSA history in this free-data build",
            "vehicleChangeover": "Sept-Nov rows flagged in event calendars for vehicle models",
            "covidMonths": "available only if source history includes 2020-03 through 2021-06",
            "gasolineBacktest": "Gasoline uses EIA weekly regular retail gasoline calendar-month average with real-time lag approximated by period date; EIA history is treated as unrevised.",
        },
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default=None)
    args = parser.parse_args()
    starts = {"custom": args.start} if args.start else WINDOWS
    for window, start in starts.items():
        result = build_window(window, start)
        out = BACKTEST_DIR / window / "results.json"
        write_json(out, result)
        print(f"Wrote {out}")


if __name__ == "__main__":
    main()
