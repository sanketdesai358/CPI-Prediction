from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .data import history_mm
from .paths import ROOT


EIA_CACHE_DIR = ROOT / "data" / "feeds" / "eia"
PASS_THROUGH_BOUNDS = {
    "diesel": (0.50, 1.15, 0.90),
    "heating_oil": (0.20, 0.90, 0.52),
}


def monthly_measurement_moves(points: list[dict[str, Any]]) -> dict[str, float]:
    values: dict[str, list[float]] = {}
    for point in points:
        date = str(point.get("date") or "")
        value = point.get("value")
        if len(date) < 7 or value is None:
            continue
        values.setdefault(date[:7], []).append(float(value))
    averages = {month: sum(month_values) / len(month_values) for month, month_values in values.items() if month_values}
    months = sorted(averages)
    moves: dict[str, float] = {}
    for idx in range(1, len(months)):
        month = months[idx]
        prior = months[idx - 1]
        if _previous_month(month) != prior or averages[prior] == 0:
            continue
        moves[month] = averages[month] / averages[prior] - 1.0
    return moves


def fit_zero_intercept_beta(
    actual_by_month: dict[str, float],
    measurement_by_month: dict[str, float],
    target_month: str,
    *,
    lower: float,
    upper: float,
    default: float,
    min_observations: int = 24,
) -> tuple[float, int]:
    pairs = [
        (float(measurement_by_month[month]), float(actual_by_month[month]))
        for month in sorted(set(actual_by_month) & set(measurement_by_month))
        if month < target_month
    ]
    if len(pairs) < min_observations:
        return default, len(pairs)
    denominator = sum(measurement * measurement for measurement, _ in pairs)
    if denominator <= 0:
        return default, len(pairs)
    beta = sum(measurement * actual for measurement, actual in pairs) / denominator
    return min(max(beta, lower), upper), len(pairs)


def measurement_forecast(
    entry: dict[str, Any],
    target_month: str,
    eia_key: str,
    raw_measurement_move: float,
) -> tuple[float, dict[str, Any]]:
    bounds = PASS_THROUGH_BOUNDS[eia_key]
    points = _load_eia_points(eia_key)
    measurement_moves = monthly_measurement_moves(points)
    actual_by_month = {
        month: float(value)
        for month, value in history_mm(entry, seasonal=False)
        if value is not None
    }
    beta, observations = fit_zero_intercept_beta(
        actual_by_month,
        measurement_moves,
        target_month,
        lower=bounds[0],
        upper=bounds[1],
        default=bounds[2],
    )
    forecast = beta * float(raw_measurement_move)
    return forecast, {
        "beta": beta,
        "observations": observations,
        "rawMeasurementMove": float(raw_measurement_move),
        "forecastNsaMm": forecast,
        "fitThrough": max((month for month in actual_by_month if month < target_month), default=None),
        "eiaSeries": eia_key,
    }


def walk_forward_rows(entry: dict[str, Any], eia_key: str, start: str = "2017-07") -> list[dict[str, Any]]:
    points = _load_eia_points(eia_key)
    measurement_moves = monthly_measurement_moves(points)
    actual_by_month = {
        month: float(value)
        for month, value in history_mm(entry, seasonal=False)
        if value is not None
    }
    rows = []
    for month in sorted(set(actual_by_month) & set(measurement_moves)):
        if month < start:
            continue
        forecast, diagnostics = measurement_forecast(entry, month, eia_key, measurement_moves[month])
        rows.append({"month": month, "actualNsaMm": actual_by_month[month], "forecastNsaMm": forecast, **diagnostics})
    return rows


def _load_eia_points(key: str) -> list[dict[str, Any]]:
    path = EIA_CACHE_DIR / f"{key}.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8")).get("points") or []


def _previous_month(month: str) -> str:
    year, mon = (int(part) for part in month.split("-"))
    mon -= 1
    if mon == 0:
        year -= 1
        mon = 12
    return f"{year:04d}-{mon:02d}"
