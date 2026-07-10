from __future__ import annotations

import json
import warnings
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import numpy as np

from .data import history_mm
from .math import add_months, month_name, safe_std
from .paths import DASHBOARD_ROOT, ROOT


LAG_WEIGHTS_PATH = ROOT / "analysis" / "used_vehicles" / "lag_weights.json"
SELECTED_MANHEIM_LAGS = [0, 2]
PASS_THROUGH_BAND = (0.30, 0.50)
VOLATILITY_THRESHOLD_PP = 1.0
MIN_MANHEIM_SCALE = 0.35
GAP_ADJUSTMENT_PER_Z_PP = 0.02
MAX_GAP_ADJUSTMENT_PP = 0.08


def load_lag_weights(path: Path = LAG_WEIGHTS_PATH) -> dict[str, Any]:
    weights = json.loads(path.read_text(encoding="utf-8"))
    betas = weights.get("manheim_lag_weights") or {}
    missing = [f"m{lag}" for lag in SELECTED_MANHEIM_LAGS if f"m{lag}" not in betas]
    if missing:
        raise ValueError(f"Used-vehicle lag weights missing required terms: {', '.join(missing)}")
    selected_sum = sum(float(betas[f"m{lag}"]) for lag in SELECTED_MANHEIM_LAGS)
    if not PASS_THROUGH_BAND[0] <= selected_sum <= PASS_THROUGH_BAND[1]:
        warnings.warn(
            "Selected SETA02 Manheim pass-through drifted outside the expected "
            f"~0.40 band: {selected_sum:.3f}",
            RuntimeWarning,
            stacklevel=2,
        )
    return weights


def cpi_release_date(target_month: str) -> date:
    calendar_path = DASHBOARD_ROOT / "src" / "data" / "release-calendar.json"
    label = month_name(target_month)
    if calendar_path.exists():
        releases = json.loads(calendar_path.read_text(encoding="utf-8"))
        for row in releases:
            if label in str(row.get("text", "")):
                return date.fromisoformat(row["releaseDate"])
    next_month = add_months(target_month, 1)
    year, month = [int(part) for part in next_month.split("-")]
    return date(year, month, 14)


def manheim_final_publication_date(month: str) -> date:
    """Estimated public month-end final date for real-time availability checks.

    Cox/Manheim publishes the free month-end UVVI workbook in the first days of
    the following month and before the CPI release. The local public feed does
    not include a historical timestamp column, so the point-in-time guard uses a
    conservative deterministic publication date: the 7th calendar day of the
    following month, rolled forward off weekends.
    """
    next_month = add_months(month, 1)
    year, raw_month = [int(part) for part in next_month.split("-")]
    published = date(year, raw_month, 7)
    while published.weekday() >= 5:
        published += timedelta(days=1)
    return published


def _month_key(raw: str) -> str:
    return raw[:7]


def _manheim_points(feed: dict[str, Any] | None) -> dict[str, float]:
    out: dict[str, float] = {}
    for point in (feed or {}).get("points") or []:
        raw_date = str(point.get("date", ""))
        if len(raw_date) < 7 or point.get("value") is None:
            continue
        out[_month_key(raw_date)] = float(point["value"])
    return dict(sorted(out.items()))


def _manheim_mom_pp(points: dict[str, float]) -> dict[str, float]:
    out: dict[str, float] = {}
    months = sorted(points)
    for month in months:
        prior = add_months(month, -1)
        if prior in points and points[prior] != 0:
            out[month] = (points[month] / points[prior] - 1.0) * 100.0
    return out


def _available_manheim_mom(feed: dict[str, Any] | None, target_month: str) -> tuple[dict[int, float], list[str]]:
    points = _manheim_points(feed)
    mom = _manheim_mom_pp(points)
    release = cpi_release_date(target_month)
    values: dict[int, float] = {}
    notes: list[str] = []
    for lag in SELECTED_MANHEIM_LAGS:
        month = add_months(target_month, -lag)
        pub = manheim_final_publication_date(month)
        if month in mom and pub < release:
            values[lag] = mom[month]
            notes.append(f"m{lag} {month} {mom[month]:+.2f}% pub {pub.isoformat()}")
        elif month not in mom:
            notes.append(f"m{lag} {month} unavailable in Manheim feed")
        else:
            notes.append(f"m{lag} {month} blocked until {pub.isoformat()}")
    return values, notes


def _level_gap_adjustment_pp(entry: dict[str, Any], manheim_points: dict[str, float]) -> tuple[float, str]:
    rows = [
        point
        for point in entry.get("history", [])
        if point.get("saIndex") is not None and _month_key(point["month"]) in manheim_points
    ]
    if len(rows) < 36 or not manheim_points:
        return 0.0, "level-gap guard unavailable"
    anchor = "2015-01"
    anchor_row = next((point for point in rows if point["month"] == anchor), None)
    anchor_manheim = manheim_points.get(anchor)
    if not anchor_row or not anchor_row.get("saIndex") or not anchor_manheim:
        anchor_row = rows[0]
        anchor_manheim = manheim_points[_month_key(anchor_row["month"])]
    gaps = []
    for point in rows:
        month = _month_key(point["month"])
        cpi_rebased = float(point["saIndex"]) / float(anchor_row["saIndex"]) * 100.0
        manheim_rebased = manheim_points[month] / anchor_manheim * 100.0
        gaps.append(cpi_rebased - manheim_rebased)
    std = float(np.std(gaps, ddof=1)) if len(gaps) > 1 else 0.0
    if std <= 0:
        return 0.0, "level-gap guard flat"
    z = (gaps[-1] - float(np.mean(gaps))) / std
    adjustment = max(
        -MAX_GAP_ADJUSTMENT_PP,
        min(MAX_GAP_ADJUSTMENT_PP, -GAP_ADJUSTMENT_PER_Z_PP * z),
    )
    return adjustment, f"level gap z={z:+.2f}, mean-reversion adj {adjustment:+.2f} pp"


def forecast_seta02_sa(entry: dict[str, Any], target_month: str, feed: dict[str, Any] | None) -> tuple[float, str] | None:
    """Forecast SETA02 SA m/m as AR persistence plus Manheim lag 0 and lag 2.

    Units inside the regression are percentage points, matching
    analysis/used_vehicles/report.md. The returned forecast is decimal m/m.
    """
    weights = load_lag_weights()
    betas = weights["manheim_lag_weights"]
    rho = float(weights["persistence_rho"])
    intercept = float(weights.get("intercept") or 0.0)
    asym = weights.get("asymmetry") or {}
    if float(asym.get("wald_equal_pvalue") or 0.0) < 0.05:
        warnings.warn("SETA02 asymmetry became significant; model currently keeps symmetric terms.", RuntimeWarning, stacklevel=2)

    sa_points = history_mm(entry, seasonal=True)
    sa_values = [float(value) for _, value in sa_points if value is not None and np.isfinite(value)]
    if not sa_values:
        return None
    y_lag1_pp = sa_values[-1] * 100.0
    recent_vol_pp = safe_std([value * 100.0 for value in sa_values[-6:]], default=VOLATILITY_THRESHOLD_PP)
    manheim_scale = max(MIN_MANHEIM_SCALE, min(1.0, recent_vol_pp / VOLATILITY_THRESHOLD_PP))

    manheim_terms, timing_notes = _available_manheim_mom(feed, target_month)
    if not manheim_terms:
        return None
    manheim_signal_pp = intercept + sum(float(betas[f"m{lag}"]) * value for lag, value in manheim_terms.items())
    persistence_pp = rho * y_lag1_pp
    gap_adjustment_pp, gap_note = _level_gap_adjustment_pp(entry, _manheim_points(feed))
    forecast_pp = persistence_pp + manheim_scale * manheim_signal_pp + gap_adjustment_pp

    used_lags = ", ".join(f"m{lag}" for lag in sorted(manheim_terms))
    omitted = sorted(set(SELECTED_MANHEIM_LAGS) - set(manheim_terms))
    omitted_note = f"; omitted unavailable {', '.join(f'm{lag}' for lag in omitted)}" if omitted else ""
    driver = (
        "SETA02 SA model: "
        f"rho {rho:.2f} * prior CPI SA {y_lag1_pp:+.2f} pp "
        f"+ Manheim {used_lags} signal {manheim_signal_pp:+.2f} pp "
        f"* volatility scale {manheim_scale:.2f} "
        f"+ {gap_note}; timing {'; '.join(timing_notes)}{omitted_note}. "
        "Compared against CUSR0000SETA02; no asymmetry term kept."
    )
    return forecast_pp / 100.0, driver
