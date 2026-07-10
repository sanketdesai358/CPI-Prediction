from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date
from statistics import NormalDist

import numpy as np


def add_months(month: str, delta: int) -> str:
    year, raw_month = [int(part) for part in month.split("-")]
    index = year * 12 + raw_month - 1 + delta
    return f"{index // 12:04d}-{index % 12 + 1:02d}"


def month_name(month: str) -> str:
    year, raw_month = month.split("-")
    return f"{calendar.month_abbr[int(raw_month)]} {year}"


def price_updated_relative_importance(
    component_dec_ri: float,
    component_index_month: float,
    component_index_dec: float,
    all_items_index_month: float,
    all_items_index_dec: float,
) -> float:
    return 100.0 * (
        component_dec_ri * (component_index_month / component_index_dec)
    ) / (100.0 * (all_items_index_month / all_items_index_dec))


def pct_change(current: float | None, prior: float | None) -> float | None:
    if current is None or prior in (None, 0):
        return None
    return current / prior - 1.0


def safe_mean(values: list[float | None], default: float = 0.0) -> float:
    clean = [float(value) for value in values if value is not None and np.isfinite(value)]
    return float(np.mean(clean)) if clean else default


def safe_std(values: list[float | None], default: float = 0.0) -> float:
    clean = [float(value) for value in values if value is not None and np.isfinite(value)]
    return float(np.std(clean, ddof=1)) if len(clean) > 1 else default


def ar1(values: list[float | None]) -> float:
    clean = np.array([float(value) for value in values if value is not None and np.isfinite(value)])
    if len(clean) < 4 or np.std(clean[:-1]) == 0 or np.std(clean[1:]) == 0:
        return 0.0
    return float(np.corrcoef(clean[:-1], clean[1:])[0, 1])


def seasonal_strength(points: list[tuple[str, float | None]]) -> float:
    clean = [(month, float(value)) for month, value in points if value is not None and np.isfinite(value)]
    if len(clean) < 24:
        return 0.0
    values = np.array([value for _, value in clean])
    total = float(np.sum((values - values.mean()) ** 2))
    if total <= 0:
        return 0.0
    by_month = {m: [] for m in range(1, 13)}
    for month, value in clean:
        by_month[int(month[-2:])].append(value)
    fitted = np.array([np.mean(by_month[int(month[-2:])]) for month, _ in clean])
    residual = float(np.sum((values - fitted) ** 2))
    return max(0.0, min(1.0, 1.0 - residual / total))


@dataclass(frozen=True)
class Interval:
    p10: float
    p50: float
    p90: float


def normal_interval(center: float, sigma: float) -> Interval:
    dist = NormalDist(mu=center, sigma=max(sigma, 1e-6))
    return Interval(
        p10=dist.inv_cdf(0.10),
        p50=center,
        p90=dist.inv_cdf(0.90),
    )
