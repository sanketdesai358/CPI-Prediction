from __future__ import annotations

import argparse
import json
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cpi_model.backtest import WINDOWS, mae, rmse
from cpi_model.data import entry_by_code, forecast_universe_codes, write_json
from cpi_model.feeds import monthly_average
from cpi_model.math import add_months, pct_change, safe_mean
from cpi_model.paths import BACKTEST_DIR, DASHBOARD_ROOT, ROOT


OUT_DIR = ROOT / "challenger" / "hrnn"
RESULT_PATH = OUT_DIR / "results.json"
REPORT_PATH = OUT_DIR / "comparison.md"
DASHBOARD_RESULT_PATH = DASHBOARD_ROOT / "src" / "data" / "challenger" / "results.json"
PRODUCTION_FORECAST_PATH = DASHBOARD_ROOT / "src" / "data" / "forecast" / "latest-forecast.json"
ALPHA = 1.5
MIN_TRAIN_MONTHS = 24
MAJOR_COMPONENT_CODES = [
    "SAF1",   # Food
    "SA0E",   # Energy
    "SAH1",   # Shelter
    "SETA02", # Used cars and trucks
    "SACL1E", # Core commodities
    "SASLE",  # Core services less energy services
    "SAT1",   # Private transportation
    "SAM",    # Medical care
    "SAR",    # Recreation
    "SAE",    # Education and communication
    "SAG",    # Other goods and services
]
CHALLENGER_VARIANTS = ["production", "productionTier1", "productionTier3", "hrnn", "iGru", "seasonalAr"]


def _series(entry: dict[str, Any]) -> list[dict[str, Any]]:
    history = entry.get("history", [])
    rows: list[dict[str, Any]] = []
    for point in history:
        prior = next((item for item in history if item["month"] == add_months(point["month"], -1)), None)
        nsa = point.get("nsaIndex")
        prior_nsa = prior.get("nsaIndex") if prior else None
        actual = None if not nsa or not prior_nsa else math.log(float(nsa) / float(prior_nsa))
        rows.append(
            {
                "month": point["month"],
                "actualNsaMm": actual,
                "actualSaMm": point.get("saMm"),
                "ri": point.get("ri") if point.get("ri") is not None else entry.get("currentRi"),
            }
        )
    return rows


def _value_before(rows: list[dict[str, Any]], month: str, key: str) -> list[float]:
    return [float(row[key]) for row in rows if row["month"] < month and row.get(key) is not None]


def _seasonal_ar(rows: list[dict[str, Any]], month: str, key: str = "actualNsaMm") -> float | None:
    values = _value_before(rows, month, key)
    if not values:
        return None
    same_month = [
        float(row[key])
        for row in rows
        if row["month"] < month and row["month"][-2:] == month[-2:] and row.get(key) is not None
    ]
    trailing = values[-6:]
    return 0.65 * safe_mean(same_month[-8:], safe_mean(trailing, 0.0)) + 0.35 * safe_mean(trailing, 0.0)


def _i_gru_proxy(rows: list[dict[str, Any]], month: str, key: str = "actualNsaMm") -> float | None:
    values = _value_before(rows, month, key)
    if len(values) < 3:
        return _seasonal_ar(rows, month, key)
    same = _seasonal_ar(rows, month, key)
    raw = 0.50 * values[-1] + 0.20 * safe_mean(values[-3:], values[-1]) + 0.20 * (same if same is not None else values[-1]) + 0.10 * safe_mean(values[-24:], values[-1])
    return math.tanh(raw / 0.08) * 0.08


def _corr(child_rows: list[dict[str, Any]], parent_rows: list[dict[str, Any]], month: str) -> float:
    parent_by_month = {row["month"]: row.get("actualNsaMm") for row in parent_rows if row["month"] < month}
    pairs = [
        (float(row["actualNsaMm"]), float(parent_by_month[row["month"]]))
        for row in child_rows
        if row["month"] < month
        and row.get("actualNsaMm") is not None
        and parent_by_month.get(row["month"]) is not None
    ][-120:]
    if len(pairs) < 12:
        return 0.0
    xs = [item[0] for item in pairs]
    ys = [item[1] for item in pairs]
    xbar = safe_mean(xs, 0.0)
    ybar = safe_mean(ys, 0.0)
    xvar = sum((x - xbar) ** 2 for x in xs)
    yvar = sum((y - ybar) ** 2 for y in ys)
    if xvar <= 0 or yvar <= 0:
        return 0.0
    return max(-0.99, min(0.99, sum((x - xbar) * (y - ybar) for x, y in pairs) / math.sqrt(xvar * yvar)))


def _gasoline_forecast(month: str) -> float | None:
    path = ROOT / "data" / "feeds" / "eia" / "gasoline_regular.json"
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    points = payload.get("points") or []
    current = monthly_average(points, month)
    prior = monthly_average(points, add_months(month, -1))
    if current is None or prior in {None, 0}:
        return None
    return math.log(float(current) / float(prior))


def _sa_offset(entry: dict[str, Any], month: str) -> float:
    nsa_rows = _series(entry)
    offsets = [
        float(row["actualSaMm"]) - float(row["actualNsaMm"])
        for row in nsa_rows
        if row["month"] < month
        and row["month"][-2:] == month[-2:]
        and row.get("actualSaMm") is not None
        and row.get("actualNsaMm") is not None
    ]
    return safe_mean(offsets[-8:], 0.0)


def _prod_component_proxy(rows: list[dict[str, Any]], month: str) -> float | None:
    values = _value_before(rows, month, "actualNsaMm")
    if not values:
        return None
    seasonal = _seasonal_ar(rows, month)
    return 0.45 * values[-1] + 0.35 * (seasonal if seasonal is not None else values[-1]) + 0.20 * safe_mean(values[-6:], values[-1])


def _production_tier_fallback(rows: list[dict[str, Any]], month: str, tier: int) -> float | None:
    values = _value_before(rows, month, "actualNsaMm")
    if not values:
        return None
    same_month = [
        float(row["actualNsaMm"])
        for row in rows
        if row["month"] < month and row["month"][-2:] == month[-2:] and row.get("actualNsaMm") is not None
    ]
    last = values[-1]
    trailing3 = safe_mean(values[-3:], last)
    trailing6 = safe_mean(values[-6:], trailing3)
    seasonal = safe_mean(same_month, trailing6)
    if tier == 1:
        return 0.55 * last + 0.30 * trailing3 + 0.15 * seasonal
    return 0.45 * last + 0.25 * trailing3 + 0.20 * seasonal + 0.10 * trailing6


def _forecast_month(
    month: str,
    entries: dict[str, dict[str, Any]],
    series_by_code: dict[str, list[dict[str, Any]]],
) -> dict[str, dict[str, float | None]]:
    by_level = sorted(entries.values(), key=lambda entry: int(entry.get("level") or 0))
    predictions: dict[str, dict[str, float | None]] = {}
    for entry in by_level:
        code = entry["itemCode"]
        rows = series_by_code[code]
        seasonal = _seasonal_ar(rows, month)
        i_gru = _i_gru_proxy(rows, month)
        if code == "SETB01":
            gas = _gasoline_forecast(month)
            if gas is not None:
                predictions[code] = {
                    "seasonalAr": gas,
                    "iGru": gas,
                    "hrnn": gas,
                    "production": gas,
                    "productionTier1": gas,
                    "productionTier3": gas,
                }
                continue
        parent = entry.get("parent")
        parent_hrnn = predictions.get(parent or "", {}).get("hrnn")
        if parent and parent_hrnn is not None and i_gru is not None:
            parent_rows = series_by_code.get(parent, [])
            corr = _corr(rows, parent_rows, month)
            tau = math.exp(ALPHA + corr)
            lam = tau / (tau + 12.0)
            hrnn = (1.0 - lam) * i_gru + lam * parent_hrnn
        else:
            hrnn = i_gru
        predictions[code] = {
            "seasonalAr": seasonal,
            "iGru": i_gru,
            "hrnn": hrnn,
            "production": _prod_component_proxy(rows, month),
            "productionTier1": _production_tier_fallback(rows, month, 1),
            "productionTier3": _production_tier_fallback(rows, month, 3),
        }
    return predictions


def _aggregate_leaf(
    month: str,
    leaf_codes: list[str],
    series_by_code: dict[str, list[dict[str, Any]]],
    predictions: dict[str, dict[str, float | None]],
    variant: str,
) -> float | None:
    weighted = 0.0
    denom = 0.0
    for code in leaf_codes:
        value = predictions.get(code, {}).get(variant)
        if value is None:
            continue
        eligible = [item for item in series_by_code[code] if item["month"] <= month]
        row = eligible[-1] if eligible else None
        weight = float(row.get("ri") or 0.0) if row else 0.0
        if weight <= 0:
            continue
        weighted += weight * float(value)
        denom += weight
    return weighted / denom if denom > 0 else None


def _metrics(rows: list[dict[str, Any]], prefix: str, actual_key: str) -> dict[str, float | None]:
    return {
        f"{prefix}Mae": mae(rows, prefix, actual_key),
        f"{prefix}Rmse": rmse(rows, prefix, actual_key),
    }


def _pct_mm_to_log(value: float | None) -> float | None:
    if value is None:
        return None
    return math.log1p(float(value))


def _implied_yoy(entry: dict[str, Any], month: str, mm: float | None, *, seasonal: bool = False) -> float | None:
    if mm is None:
        return None
    prior_month = add_months(month, -1)
    year_ago = add_months(month, -12)
    prior = next((point for point in entry.get("history", []) if point["month"] == prior_month), None)
    base = next((point for point in entry.get("history", []) if point["month"] == year_ago), None)
    key = "saIndex" if seasonal else "nsaIndex"
    if not prior or not base or not prior.get(key) or not base.get(key):
        return None
    return (float(prior[key]) * math.exp(float(mm))) / float(base[key]) - 1.0


def _actual_measures(entry: dict[str, Any], month: str) -> dict[str, float | None]:
    history = entry.get("history", [])
    current = next((point for point in history if point["month"] == month), None)
    prior = next((point for point in history if point["month"] == add_months(month, -1)), None)
    year_ago = next((point for point in history if point["month"] == add_months(month, -12)), None)
    if not current:
        return {"nsaMm": None, "saMm": None, "nsaYoy": None, "saYoy": None}
    return {
        "nsaMm": pct_change(current.get("nsaIndex"), prior.get("nsaIndex") if prior else None),
        "saMm": current.get("saMm"),
        "nsaYoy": pct_change(current.get("nsaIndex"), year_ago.get("nsaIndex") if year_ago else None),
        "saYoy": pct_change(current.get("saIndex"), year_ago.get("saIndex") if year_ago else None),
    }


def _model_measures(entry: dict[str, Any], month: str, nsa_mm: float | None) -> dict[str, float | None]:
    sa_mm = None if nsa_mm is None else nsa_mm + _sa_offset(entry, month)
    return {
        "nsaMm": nsa_mm,
        "saMm": sa_mm,
        "nsaYoy": _implied_yoy(entry, month, nsa_mm, seasonal=False),
        "saYoy": _implied_yoy(entry, month, sa_mm, seasonal=True),
    }


def _production_measures(forecast: dict[str, Any], series: str) -> dict[str, float | None]:
    row = forecast.get(series) or {}
    return {
        "nsaMm": _pct_mm_to_log(row.get("nsaMm")),
        "saMm": _pct_mm_to_log(row.get("saMm")),
        "nsaYoy": row.get("nsaYoy"),
        "saYoy": row.get("saYoy"),
    }


def _production_component_measures(row: dict[str, Any]) -> dict[str, float | None]:
    return {
        "nsaMm": row.get("forecast_nsa_mm"),
        "saMm": row.get("forecast_sa_mm"),
        "nsaYoy": row.get("component_yoy"),
        "saYoy": None,
    }


def _prediction_measure_row(
    entry: dict[str, Any],
    month: str,
    predictions: dict[str, dict[str, float | None]],
    code: str,
    *,
    actual: bool,
) -> dict[str, Any]:
    out: dict[str, Any] = {
        "actual": _actual_measures(entry, month) if actual else {"nsaMm": None, "saMm": None, "nsaYoy": None, "saYoy": None}
    }
    for variant in CHALLENGER_VARIANTS:
        out[variant] = _model_measures(entry, month, predictions.get(code, {}).get(variant))
    return out


def _current_forecast(
    entries: dict[str, dict[str, Any]],
    series_by_code: dict[str, list[dict[str, Any]]],
    leaf_codes: list[str],
) -> dict[str, Any] | None:
    if not PRODUCTION_FORECAST_PATH.exists():
        return None
    production = json.loads(PRODUCTION_FORECAST_PATH.read_text(encoding="utf-8"))
    month = production.get("forecastMonth")
    if not month:
        return None
    predictions = _forecast_month(month, entries, series_by_code)
    headline_nsa = {
        "productionTier1": _aggregate_leaf(month, leaf_codes, series_by_code, predictions, "productionTier1"),
        "productionTier3": _aggregate_leaf(month, leaf_codes, series_by_code, predictions, "productionTier3"),
        "hrnn": _aggregate_leaf(month, leaf_codes, series_by_code, predictions, "hrnn"),
        "iGru": _aggregate_leaf(month, leaf_codes, series_by_code, predictions, "iGru"),
        "seasonalAr": _aggregate_leaf(month, leaf_codes, series_by_code, predictions, "seasonalAr"),
    }
    core_nsa = {
        "productionTier1": predictions.get("SA0L1E", {}).get("productionTier1"),
        "productionTier3": predictions.get("SA0L1E", {}).get("productionTier3"),
        "hrnn": predictions.get("SA0L1E", {}).get("hrnn"),
        "iGru": predictions.get("SA0L1E", {}).get("iGru"),
        "seasonalAr": predictions.get("SA0L1E", {}).get("seasonalAr"),
    }
    major_rows = []
    for code in MAJOR_COMPONENT_CODES:
        entry = entries.get(code)
        if not entry or code not in series_by_code:
            continue
        major_rows.append(
            {
                "series": code,
                "label": entry["name"],
                "weight": entry.get("currentRi"),
                **_prediction_measure_row(entry, month, predictions, code, actual=False),
            }
        )

    component_rows = []
    for component in production.get("components", []):
        code = component.get("itemCode")
        entry = entries.get(code)
        if not code or not entry or code not in series_by_code:
            continue
        prediction_row = _prediction_measure_row(entry, month, predictions, code, actual=False)
        prediction_row["production"] = _production_component_measures(component)
        component_rows.append(
            {
                "series": code,
                "label": component.get("name") or entry["name"],
                "weight": component.get("blsCurrentRi") if component.get("blsCurrentRi") is not None else entry.get("currentRi"),
                "modelType": component.get("modelType"),
                "tier": component.get("tier"),
                "driverSnapshot": component.get("driverSnapshot"),
                **prediction_row,
            }
        )

    def row(series: str, label: str, entry_code: str, challenger_nsa: dict[str, float | None]) -> dict[str, Any]:
        entry = entries[entry_code]
        return {
            "series": series,
            "label": label,
            "actual": _actual_measures(entry, month),
            "production": _production_measures(production, series),
            "productionTier1": _model_measures(entry, month, challenger_nsa["productionTier1"]),
            "productionTier3": _model_measures(entry, month, challenger_nsa["productionTier3"]),
            "hrnn": _model_measures(entry, month, challenger_nsa["hrnn"]),
            "iGru": _model_measures(entry, month, challenger_nsa["iGru"]),
            "seasonalAr": _model_measures(entry, month, challenger_nsa["seasonalAr"]),
        }

    return {
        "forecastMonth": month,
        "dataThrough": production.get("dataThrough"),
        "source": "Production values come from latest-forecast.json; challenger values are precomputed endogenous research outputs. Actual is populated only when that CPI month is in the local BLS cache.",
        "rows": [
            row("headline", "Headline CPI", "SA0", headline_nsa),
            row("core", "Core CPI", "SA0L1E", core_nsa),
        ],
        "majorRows": major_rows,
        "componentRows": component_rows,
    }


def build_comparison() -> dict[str, Any]:
    started = time.perf_counter()
    entries = entry_by_code()
    series_by_code = {code: _series(entry) for code, entry in entries.items() if entry.get("history")}
    leaf_codes = [code for code in forecast_universe_codes(list(entries.values())) if code in series_by_code]
    headline = series_by_code["SA0"]
    core = series_by_code.get("SA0L1E", [])
    months = [row["month"] for row in headline if row.get("actualNsaMm") is not None]
    rows: list[dict[str, Any]] = []
    component_errors: dict[str, list[dict[str, Any]]] = {code: [] for code in leaf_codes}
    component_series: dict[str, list[dict[str, Any]]] = {code: [] for code in leaf_codes}
    major_component_errors: dict[str, list[dict[str, Any]]] = {
        code: [] for code in MAJOR_COMPONENT_CODES if code in series_by_code
    }

    for month in months:
        if len([item for item in headline if item["month"] < month and item.get("actualNsaMm") is not None]) < MIN_TRAIN_MONTHS:
            continue
        predictions = _forecast_month(month, entries, series_by_code)
        headline_row = next(row for row in headline if row["month"] == month)
        core_row = next((row for row in core if row["month"] == month), None)
        headline_entry = entries["SA0"]
        core_entry = entries.get("SA0L1E", headline_entry)
        row = {
            "month": month,
            "actualHeadlineNsaMm": headline_row.get("actualNsaMm"),
            "actualHeadlineSaMm": headline_row.get("actualSaMm"),
            "actualCoreNsaMm": core_row.get("actualNsaMm") if core_row else None,
            "actualCoreSaMm": core_row.get("actualSaMm") if core_row else None,
            "productionHeadlineNsaMm": _aggregate_leaf(month, leaf_codes, series_by_code, predictions, "production"),
            "productionTier1HeadlineNsaMm": _aggregate_leaf(month, leaf_codes, series_by_code, predictions, "productionTier1"),
            "productionTier3HeadlineNsaMm": _aggregate_leaf(month, leaf_codes, series_by_code, predictions, "productionTier3"),
            "hrnnHeadlineNsaMm": _aggregate_leaf(month, leaf_codes, series_by_code, predictions, "hrnn"),
            "iGruHeadlineNsaMm": _aggregate_leaf(month, leaf_codes, series_by_code, predictions, "iGru"),
            "seasonalArHeadlineNsaMm": _aggregate_leaf(month, leaf_codes, series_by_code, predictions, "seasonalAr"),
            "hrnnAggregateNodeNsaMm": predictions.get("SA0", {}).get("hrnn"),
            "iGruAggregateNodeNsaMm": predictions.get("SA0", {}).get("iGru"),
            "seasonalArAggregateNodeNsaMm": predictions.get("SA0", {}).get("seasonalAr"),
            "productionCoreNsaMm": predictions.get("SA0L1E", {}).get("production"),
            "productionTier1CoreNsaMm": predictions.get("SA0L1E", {}).get("productionTier1"),
            "productionTier3CoreNsaMm": predictions.get("SA0L1E", {}).get("productionTier3"),
            "hrnnCoreNsaMm": predictions.get("SA0L1E", {}).get("hrnn"),
            "iGruCoreNsaMm": predictions.get("SA0L1E", {}).get("iGru"),
            "seasonalArCoreNsaMm": predictions.get("SA0L1E", {}).get("seasonalAr"),
        }
        for prefix, entry in [("Headline", headline_entry), ("Core", core_entry)]:
            offset = _sa_offset(entry, month)
            actual_key = f"actual{prefix}NsaMm"
            if row.get(actual_key) is not None:
                for variant in ["production", "productionTier1", "productionTier3", "hrnn", "iGru", "seasonalAr"]:
                    nsa_key = f"{variant}{prefix}NsaMm"
                    row[f"{variant}{prefix}SaMm"] = None if row.get(nsa_key) is None else float(row[nsa_key]) + offset
        rows.append(row)

        for code in major_component_errors:
            actual = next((item for item in series_by_code[code] if item["month"] == month), None)
            if not actual or actual.get("actualNsaMm") is None:
                continue
            entry = entries[code]
            offset = _sa_offset(entry, month)
            item = {
                "month": month,
                "actualNsaMm": actual.get("actualNsaMm"),
                "actualSaMm": actual.get("actualSaMm"),
            }
            for variant in CHALLENGER_VARIANTS:
                nsa = predictions.get(code, {}).get(variant)
                item[f"{variant}NsaMm"] = nsa
                item[f"{variant}SaMm"] = None if nsa is None else float(nsa) + offset
            major_component_errors[code].append(item)

        for code in leaf_codes:
            actual = next((item for item in series_by_code[code] if item["month"] == month), None)
            if not actual or actual.get("actualNsaMm") is None:
                continue
            pred = predictions.get(code, {})
            item = {
                "month": month,
                "actualNsaMm": actual.get("actualNsaMm"),
                "actualSaMm": actual.get("actualSaMm"),
                "productionNsaMm": pred.get("production"),
                "hrnnNsaMm": pred.get("hrnn"),
                "iGruNsaMm": pred.get("iGru"),
                "seasonalArNsaMm": pred.get("seasonalAr"),
            }
            component_series[code].append(item)
            component_errors[code].append(item)

    windows: dict[str, Any] = {}
    for label, start in WINDOWS.items():
        window_rows = [row for row in rows if row["month"] >= start]
        rolling = []
        for index, row in enumerate(window_rows):
            span = window_rows[max(0, index - 23) : index + 1]
            rolling.append({"month": row["month"], "production": mae(span, "productionHeadlineNsaMm", "actualHeadlineNsaMm"), "productionTier1": mae(span, "productionTier1HeadlineNsaMm", "actualHeadlineNsaMm"), "productionTier3": mae(span, "productionTier3HeadlineNsaMm", "actualHeadlineNsaMm"), "hrnn": mae(span, "hrnnHeadlineNsaMm", "actualHeadlineNsaMm"), "iGru": mae(span, "iGruHeadlineNsaMm", "actualHeadlineNsaMm"), "seasonalAr": mae(span, "seasonalArHeadlineNsaMm", "actualHeadlineNsaMm")})
        metrics: dict[str, float | None] = {}
        for variant in ["production", "productionTier1", "productionTier3", "hrnn", "iGru", "seasonalAr"]:
            metrics.update(_metrics(window_rows, f"{variant}HeadlineNsaMm", "actualHeadlineNsaMm"))
            metrics.update(_metrics(window_rows, f"{variant}HeadlineSaMm", "actualHeadlineSaMm"))
            metrics.update(_metrics(window_rows, f"{variant}CoreNsaMm", "actualCoreNsaMm"))
            metrics.update(_metrics(window_rows, f"{variant}CoreSaMm", "actualCoreSaMm"))
        windows[label] = {"requestedStart": start, "availableStart": window_rows[0]["month"] if window_rows else None, "availableEnd": window_rows[-1]["month"] if window_rows else None, "metrics": metrics, "rolling24": rolling}

    production_backtests = {}
    for label in WINDOWS:
        path = BACKTEST_DIR / label / "results.json"
        if path.exists():
            production_backtests[label] = json.loads(path.read_text(encoding="utf-8")).get("metrics", {})

    league = []
    for code in leaf_codes:
        entry = entries[code]
        all_rows = component_errors[code]
        c_rows = [row for row in all_rows if row["month"] >= WINDOWS["C"]]
        b_rows = [row for row in all_rows if row["month"] >= WINDOWS["B"]]
        prod_mae = mae(c_rows, "productionNsaMm", "actualNsaMm")
        hrnn_mae = mae(c_rows, "hrnnNsaMm", "actualNsaMm")
        i_mae = mae(c_rows, "iGruNsaMm", "actualNsaMm")
        s_mae = mae(c_rows, "seasonalArNsaMm", "actualNsaMm")
        if prod_mae is None or hrnn_mae is None:
            continue
        best_model = min(
            [
                ("Production", prod_mae),
                ("HRNN", hrnn_mae),
                ("I-GRU", i_mae if i_mae is not None else 99.0),
                ("Seasonal AR", s_mae if s_mae is not None else 99.0),
            ],
            key=lambda item: item[1],
        )
        challenger_values = [value for value in [hrnn_mae, i_mae, s_mae] if value is not None]
        best_challenger_mae = min(challenger_values) if challenger_values else None
        gap = 0.0 if best_challenger_mae is None else prod_mae - best_challenger_mae
        second_best = sorted(
            [
                prod_mae,
                hrnn_mae,
                i_mae if i_mae is not None else 99.0,
                s_mae if s_mae is not None else 99.0,
            ]
        )[1]
        if abs(second_best - best_model[1]) < 0.0002:
            verdict = "TIE"
        else:
            verdict = f"{best_model[0].upper()} WINS"
        b_gap = None
        if b_rows:
            b_prod = mae(b_rows, "productionNsaMm", "actualNsaMm")
            b_hrnn = mae(b_rows, "hrnnNsaMm", "actualNsaMm")
            b_gap = None if b_prod is None or b_hrnn is None else b_prod - b_hrnn
        weight = float(entry.get("currentRi") or 0.0)
        league.append(
            {
                "itemCode": code,
                "name": entry["name"],
                "level": entry.get("level"),
                "weight": weight,
                "productionMae": prod_mae,
                "hrnnMae": hrnn_mae,
                "iGruMae": i_mae,
                "seasonalArMae": s_mae,
                "bestModel": best_model[0],
                "bestChallenger": "Seasonal AR" if best_challenger_mae == s_mae else "I-GRU" if best_challenger_mae == i_mae else "HRNN",
                "verdict": verdict,
                "weightedGap": weight * abs(gap),
                "windowBHrnnGap": b_gap,
            }
        )
    league.sort(key=lambda row: row["weightedGap"], reverse=True)

    hierarchy = []
    for level in sorted({int(entry.get("level") or 0) for entry in entries.values()}):
        level_codes = [code for code in leaf_codes if int(entries[code].get("level") or 0) == level]
        level_rows = [row for code in level_codes for row in component_errors[code] if row["month"] >= WINDOWS["C"]]
        if not level_rows:
            continue
        ar_mae = mae(level_rows, "seasonalArNsaMm", "actualNsaMm")
        hrnn_mae = mae(level_rows, "hrnnNsaMm", "actualNsaMm")
        hierarchy.append(
            {
                "level": level,
                "components": len(level_codes),
                "hrnnMae": hrnn_mae,
                "seasonalArMae": ar_mae,
                "normalizedVsSeasonalAr": None if not ar_mae or hrnn_mae is None else hrnn_mae / ar_mae,
            }
        )

    major_diagnostics = []
    for code in MAJOR_COMPONENT_CODES:
        entry = entries.get(code)
        all_rows = major_component_errors.get(code, [])
        c_rows = [row for row in all_rows if row["month"] >= WINDOWS["C"]]
        latest = all_rows[-1] if all_rows else None
        if not entry or not c_rows or not latest:
            continue
        metrics = {}
        latest_error = {}
        latest_prediction = {}
        for variant in CHALLENGER_VARIANTS:
            metrics[variant] = {
                "saMmMae": mae(c_rows, f"{variant}SaMm", "actualSaMm"),
                "nsaMmMae": mae(c_rows, f"{variant}NsaMm", "actualNsaMm"),
            }
            latest_prediction[variant] = {
                "saMm": latest.get(f"{variant}SaMm"),
                "nsaMm": latest.get(f"{variant}NsaMm"),
            }
            latest_error[variant] = {
                "saMm": None if latest.get(f"{variant}SaMm") is None or latest.get("actualSaMm") is None else latest[f"{variant}SaMm"] - latest["actualSaMm"],
                "nsaMm": None if latest.get(f"{variant}NsaMm") is None or latest.get("actualNsaMm") is None else latest[f"{variant}NsaMm"] - latest["actualNsaMm"],
            }
        major_diagnostics.append(
            {
                "itemCode": code,
                "name": entry["name"],
                "weight": entry.get("currentRi"),
                "latestActualMonth": latest["month"],
                "latestActual": {"saMm": latest.get("actualSaMm"), "nsaMm": latest.get("actualNsaMm")},
                "latestPrediction": latest_prediction,
                "latestError": latest_error,
                "windowC": metrics,
            }
        )

    candidates = [
        {
            "itemCode": row["itemCode"],
            "name": row["name"],
            "evidence": f"HRNN beats production proxy in window C by {(row['productionMae'] - row['hrnnMae']) * 100:.2f} pp m/m; window B gap {((row['windowBHrnnGap'] or 0) * 100):.2f} pp.",
        }
        for row in league
        if row["bestModel"] == "HRNN" and row.get("windowBHrnnGap") is not None and row["windowBHrnnGap"] > 0
    ][:12]

    payload = {
        "generatedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "complete_fast_research_run",
        "implementationStatus": "Deterministic HRNN-style challenger artifact. Full PyTorch MAP checkpoint sweep remains a follow-up using this schema.",
        "source": "model output, not BLS data; research comparison only",
        "variantLabels": {"production": "Legacy proxy (not full model)", "productionTier1": "Production Tier 1 fallback", "productionTier3": "Production Tier 3 fallback", "hrnn": "HRNN", "iGru": "I-GRU", "seasonalAr": "Seasonal AR"},
        "windows": windows,
        "currentForecast": _current_forecast(entries, series_by_code, leaf_codes),
        "productionBacktestMetrics": production_backtests,
        "rows": rows,
        "componentLeague": league,
        "componentSeries": {code: rows for code, rows in component_series.items() if rows},
        "majorComponentSeries": {code: rows for code, rows in major_component_errors.items() if rows},
        "majorComponentDiagnostics": major_diagnostics,
        "hierarchyLevelMetrics": hierarchy,
        "adoptionCandidates": candidates,
        "honestNotes": [
            "Production component MAE in this first artifact is a tier-style endogenous proxy, because the existing production backtest artifact stores headline rows but not a full per-component historical forecast panel.",
            "Aggregate-node challenger forecasts can look better than bottom-up rows because they forecast published aggregates directly; bottom-up leaf aggregation is the apples-to-apples view.",
            "Window A undercredits production external feeds that did not have current local cached histories before modern feed availability.",
            "The current BLS hierarchy is applied across history; historical parent changes are documented rather than reconstructed.",
        ],
        "runtime": {"seconds": round(time.perf_counter() - started, 3), "checkpointReuse": "quarter labels are deterministic; neural warm-start checkpoints not emitted by the fast runner"},
    }
    return payload


def write_report(payload: dict[str, Any]) -> None:
    c = payload["windows"].get("C", {})
    metrics = c.get("metrics", {})
    lines = [
        "# HRNN Challenger Comparison",
        "",
        "Research comparison only. Not used in production forecasts.",
        "",
        f"Generated: {payload['generatedAt']}",
        "",
        "## Implementation status",
        "",
        payload["implementationStatus"],
        "",
        "## Window C headline scoreboard",
        "",
        "| Model | Headline NSA MAE | Headline SA MAE | Core NSA MAE | Core SA MAE |",
        "|---|---:|---:|---:|---:|",
    ]
    for variant, label in payload["variantLabels"].items():
        lines.append(
            "| {label} | {hnsa:.4f} | {hsa:.4f} | {cnsa:.4f} | {csa:.4f} |".format(
                label=label,
                hnsa=metrics.get(f"{variant}HeadlineNsaMmMae") or 0,
                hsa=metrics.get(f"{variant}HeadlineSaMmMae") or 0,
                cnsa=metrics.get(f"{variant}CoreNsaMmMae") or 0,
                csa=metrics.get(f"{variant}CoreSaMmMae") or 0,
            )
        )
    lines.extend(
        [
            "",
            "## Component league table",
            "",
            "| Component | Verdict | Best model | Weight | Production MAE | HRNN MAE | I-GRU MAE | Seasonal AR MAE |",
            "|---|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in payload["componentLeague"][:80]:
        lines.append(
            "| {name} | {verdict} | {best} | {weight:.3f} | {prod:.4f} | {hrnn:.4f} | {igru:.4f} | {sar:.4f} |".format(
                name=str(row["name"]).replace("|", "/"),
                verdict=row["verdict"],
                best=row["bestModel"],
                weight=row["weight"],
                prod=row["productionMae"] or 0,
                hrnn=row["hrnnMae"] or 0,
                igru=row["iGruMae"] or 0,
                sar=row["seasonalArMae"] or 0,
            )
        )
    lines.extend(["", "## Adoption candidates", ""])
    if payload["adoptionCandidates"]:
        for row in payload["adoptionCandidates"]:
            lines.append(f"- {row['itemCode']} {row['name']}: {row['evidence']}")
    else:
        lines.append("- None yet under the current proxy-run evidence rule.")
    lines.extend(["", "## Honest notes", ""])
    for note in payload["honestNotes"]:
        lines.append(f"- {note}")
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dashboard", action="store_true", help="Also copy results to cpi-dashboard/src/data/challenger.")
    args = parser.parse_args()
    payload = build_comparison()
    write_json(RESULT_PATH, payload)
    write_report(payload)
    if args.dashboard:
        write_json(DASHBOARD_RESULT_PATH, payload)
    print(f"Wrote {RESULT_PATH}")
    print(f"Wrote {REPORT_PATH}")
    if args.dashboard:
        print(f"Wrote {DASHBOARD_RESULT_PATH}")


if __name__ == "__main__":
    main()
