from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .data import history_mm, load_registry, write_json
from .math import add_months, pct_change, safe_mean, safe_std
from .paths import ROOT, RUNS_DIR


COMMODITY_DIR = ROOT / "data" / "feeds" / "commodity_complex"


@dataclass(frozen=True)
class CommodityMapping:
    code: str
    complex_name: str
    latent_factor: str
    cuts: tuple[str, ...]
    validator: str | None
    expected_lags: tuple[int, ...] = (0, 1, 2, 3)
    notes: str = ""


COMMODITY_MAPPINGS: tuple[CommodityMapping, ...] = (
    CommodityMapping("SEFD01", "PORK", "USDA pork cutout carcass", ("USDA pork cutout belly",), "bacon", notes="Belly primal maps to bacon and related products."),
    CommodityMapping("SEFD02", "PORK", "USDA pork cutout carcass", ("USDA pork cutout ham",), None, notes="Ham primal maps to ham."),
    CommodityMapping("SEFD03", "PORK", "USDA pork cutout carcass", ("USDA pork cutout loin",), None, notes="Loin primal maps to pork chops."),
    CommodityMapping("SEFD04", "PORK", "USDA pork cutout carcass", ("USDA pork cutout carcass",), None, notes="Composite pork cutout maps to other pork."),
    CommodityMapping("SEFC01", "BEEF", "USDA boxed beef Choice cutout", ("USDA boxed beef Choice primal Chuck", "USDA boxed beef Choice primal Round", "USDA boxed beef Choice/Select spread"), "ground_beef", notes="Chuck and round primals map to ground beef; Choice-Select spread is a quality-mix signal."),
    CommodityMapping("SEFC02", "BEEF", "USDA boxed beef Choice cutout", ("USDA boxed beef Choice primal Chuck", "USDA boxed beef Choice primal Round", "USDA boxed beef Choice/Select spread"), None, notes="Chuck and round primals map to roast-heavy beef cuts."),
    CommodityMapping("SEFC03", "BEEF", "USDA boxed beef Choice cutout", ("USDA boxed beef Choice primal Loin", "USDA boxed beef Choice primal Rib", "USDA boxed beef Choice/Select spread"), None, notes="Loin and rib primals map to steaks."),
    CommodityMapping("SEFC04", "BEEF", "USDA boxed beef Choice cutout", ("USDA boxed beef Choice cutout", "USDA boxed beef Choice/Select spread"), None, notes="Choice cutout plus quality spread maps to other beef and veal."),
    CommodityMapping("SEFF01", "POULTRY", "USDA chicken National composite whole bird", ("USDA chicken National composite whole bird", "USDA chicken National composite WOGS", "USDA chicken Boneless skinless breast", "USDA chicken Leg quarters bulk", "USDA chicken Whole wings"), "chicken", notes="Whole bird/WOGS and a spend-weighted parts basket map to chicken."),
    CommodityMapping("SEFF02", "POULTRY", "USDA chicken National composite whole bird", ("USDA chicken Boneless skinless breast", "USDA chicken Leg quarters bulk", "USDA chicken Whole wings"), None, notes="Parts composite maps to other uncooked poultry including turkey as the closest RI-bearing public stratum."),
    CommodityMapping("SEFJ01", "DAIRY", "USDA advanced Base Class I milk price", ("USDA advanced Base Class I milk price",), "milk", expected_lags=(1,), notes="Advanced Class I price is calendar-known and enters fresh milk with an approximate one-month retail lag."),
    CommodityMapping("SEFJ02", "DAIRY", "USDA NDPSR Cheddar 40-pound blocks", ("USDA NDPSR Cheddar 40-pound blocks",), None, notes="NDPSR cheddar blocks map to cheese and related products; CME spot cheese can be added when available."),
    CommodityMapping("SEFS01", "DAIRY", "USDA NDPSR Butter", ("USDA NDPSR Butter",), None, notes="NDPSR butter maps to butter and margarine."),
    CommodityMapping("SEFJ03", "DAIRY", "USDA NDPSR Nonfat dry milk", ("USDA NDPSR Nonfat dry milk", "USDA NDPSR Dry whey"), None, notes="NFDM and dry whey are cost inputs for ice cream."),
    CommodityMapping("SEFJ04", "DAIRY", "USDA NDPSR Nonfat dry milk", ("USDA NDPSR Nonfat dry milk", "USDA NDPSR Dry whey", "USDA Class III milk price", "USDA Class IV milk price"), None, notes="NFDM, dry whey, and class prices map to other dairy costs."),
    CommodityMapping("SEFH", "EGGS", "USDA combined regional caged white Large eggs midpoint", ("USDA combined regional caged white Large eggs midpoint", "USDA combined regional caged white Extra Large eggs midpoint", "USDA combined regional caged white Medium eggs midpoint"), "eggs", notes="Large midpoint is primary; Extra Large/Medium spread is a shortage-stress signal. Existing asymmetric pass-through is preserved."),
)


RESOLUTION_TARGETS: dict[str, str] = {
    "bacon": "Bacon, breakfast sausage, and related products",
    "ham": "Ham",
    "pork_chops": "Pork chops",
    "other_pork": "Other pork including roasts, steaks, and ribs",
    "ground_beef": "Uncooked ground beef",
    "beef_roasts": "Uncooked beef roasts",
    "beef_steaks": "Uncooked beef steaks",
    "other_beef": "Uncooked other beef and veal",
    "fresh_whole_chicken": "Fresh whole chicken",
    "chicken_parts": "Fresh and frozen chicken parts",
    "fresh_milk": "Milk",
    "cheese": "Cheese and related products",
    "butter": "Butter and margarine",
    "ice_cream": "Ice cream and related products",
    "eggs": "Eggs",
}


def _slug(label: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", label.lower()).strip("_")


def resolve_food_substrata(cache_by_code: dict[str, dict[str, Any]] | None = None) -> dict[str, dict[str, Any]]:
    registry = load_registry()
    cache_by_code = cache_by_code or {}
    resolved: dict[str, dict[str, Any]] = {}
    for target, name in RESOLUTION_TARGETS.items():
        matches = [row for row in registry if row.get("name") == name]
        if not matches:
            raise ValueError(f"Could not resolve CPI food sub-stratum from cu.item: {name}")
        row = matches[0]
        cache_entry = cache_by_code.get(row["item_code"])
        resolved[target] = {
            "itemCode": row["item_code"],
            "name": row["name"],
            "parent": row.get("parent"),
            "currentRi": None if cache_entry is None else cache_entry.get("currentRi"),
            "forecastable": bool(cache_entry and cache_entry.get("currentRi") is not None and cache_entry.get("seriesNsa")),
        }
    return resolved


def cut_series_from_feed_health(feed_health: dict[str, Any]) -> dict[str, dict[str, Any]]:
    series: dict[str, dict[str, Any]] = {}
    for component in feed_health.get("components", []):
        for obs in component.get("observationsUsed", []):
            label = str(obs.get("label") or "")
            if not label.startswith(("USDA ", "BLS AP ")):
                continue
            key = _slug(label)
            point = {
                "date": obs.get("date"),
                "value": obs.get("value"),
                "label": label,
                "sourceComponent": component.get("itemCode"),
                "sourceFeed": component.get("primaryFeed"),
            }
            entry = series.setdefault(key, {"label": label, "points": []})
            if point not in entry["points"]:
                entry["points"].append(point)
    for entry in series.values():
        entry["points"] = sorted(entry["points"], key=lambda item: str(item.get("date") or ""))
    return series


def write_cut_series(feed_health: dict[str, Any]) -> dict[str, dict[str, Any]]:
    series = cut_series_from_feed_health(feed_health)
    write_json(COMMODITY_DIR / "cut_series.json", {"series": series})
    return series


def _find_observation(feed_status: dict[str, Any] | None, label: str) -> dict[str, Any] | None:
    if not feed_status:
        return None
    for obs in feed_status.get("observationsUsed", []):
        if str(obs.get("label")) == label:
            return obs
    return None


def _mean_observation(feed_status: dict[str, Any] | None, labels: tuple[str, ...]) -> float | None:
    values = []
    for label in labels:
        obs = _find_observation(feed_status, label)
        if obs and obs.get("value") is not None:
            values.append(float(obs["value"]))
    return safe_mean(values, None) if values else None


def _history_forecast(entry: dict[str, Any], target_month: str) -> float:
    points = history_mm(entry, seasonal=False)
    values = [value for _, value in points if value is not None]
    last = values[-1] if values else 0.0
    trailing3 = safe_mean(values[-3:], last)
    trailing6 = safe_mean(values[-6:], trailing3)
    seasonal = safe_mean([value for month, value in points if month[-2:] == target_month[-2:]], trailing6)
    return 0.45 * last + 0.25 * trailing3 + 0.20 * seasonal + 0.10 * trailing6


def _lag_profile(entry: dict[str, Any], complex_entry: dict[str, Any] | None) -> dict[str, Any]:
    child = dict(history_mm(entry, seasonal=False))
    complex_points = dict(history_mm(complex_entry, seasonal=False)) if complex_entry else {}
    best_lag = 1
    best_corr: float | None = None
    for lag in range(4):
        pairs = []
        for month, y in child.items():
            x = complex_points.get(add_months(month, -lag))
            if x is not None and y is not None:
                pairs.append((float(x), float(y)))
        if len(pairs) < 12:
            continue
        xs = np.array([x for x, _ in pairs])
        ys = np.array([y for _, y in pairs])
        if np.std(xs) == 0 or np.std(ys) == 0:
            continue
        corr = float(np.corrcoef(xs, ys)[0, 1])
        if best_corr is None or abs(corr) > abs(best_corr):
            best_lag = lag
            best_corr = corr
    child_sigma = safe_std(list(child.values()), 0.0)
    complex_sigma = safe_std(list(complex_points.values()), child_sigma or 0.001)
    raw_loading = 1.0 if not complex_sigma else child_sigma / complex_sigma
    loading = max(0.15, min(1.50, 0.65 * raw_loading + 0.35))
    return {"lag": best_lag, "loading": loading, "correlation": best_corr}


def _ap_series(name: str | None) -> list[tuple[str, float | None]]:
    if not name:
        return []
    path = ROOT / "data" / "feeds" / "bls" / f"ap_{name}.csv"
    if not path.exists():
        return []
    df = pd.read_csv(path)
    if "month" not in df.columns or "value" not in df.columns:
        return []
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    rows = df.dropna(subset=["value"]).sort_values("month")
    return [(str(row["month"]), float(row["value"])) for _, row in rows.iterrows()]


def _pct_series(points: list[tuple[str, float | None]]) -> dict[str, float | None]:
    out: dict[str, float | None] = {}
    by_month = dict(points)
    for month, value in points:
        out[month] = pct_change(value, by_month.get(add_months(month, -1)))
    return out


def _correlation(a: dict[str, float | None], b: dict[str, float | None]) -> float | None:
    pairs = [(a[month], b.get(month)) for month in a if a.get(month) is not None and b.get(month) is not None]
    if len(pairs) < 12:
        return None
    xs = np.array([float(x) for x, _ in pairs])
    ys = np.array([float(y) for _, y in pairs])
    if np.std(xs) == 0 or np.std(ys) == 0:
        return None
    return float(np.corrcoef(xs, ys)[0, 1])


def validation_for(mapping: CommodityMapping, entry: dict[str, Any]) -> dict[str, Any]:
    ap_points = _ap_series(mapping.validator)
    ap_mm = _pct_series(ap_points)
    cpi_mm = dict(history_mm(entry, seasonal=False))
    return {
        "validator": mapping.validator,
        "wholesaleApCorrelation": None,
        "apCpiCorrelation": _correlation(ap_mm, cpi_mm),
        "note": "Wholesale-to-AP correlation requires a historical USDA cut archive; AP-to-CPI correlation uses local BLS AP validator history where available.",
    }


def _live_cut_adjustment(mapping: CommodityMapping, feed_status: dict[str, Any] | None) -> float:
    factor = _find_observation(feed_status, mapping.latent_factor)
    cut_mean = _mean_observation(feed_status, mapping.cuts)
    if not factor or factor.get("value") in (None, 0) or cut_mean is None:
        return 0.0
    relative_level = cut_mean / float(factor["value"]) - 1.0
    adjustment = max(-0.0020, min(0.0020, 0.010 * relative_level))
    if mapping.code == "SEFH":
        large = _find_observation(feed_status, "USDA combined regional caged white Large eggs midpoint")
        xl = _find_observation(feed_status, "USDA combined regional caged white Extra Large eggs midpoint")
        medium = _find_observation(feed_status, "USDA combined regional caged white Medium eggs midpoint")
        if large and xl and medium and large.get("value") not in (None, 0):
            stress = (float(xl["value"]) - float(medium["value"])) / float(large["value"])
            adjustment += max(0.0, min(0.0030, 0.010 * stress))
    return adjustment


def forecast_commodity_component(
    entry: dict[str, Any],
    target_month: str,
    cache_by_code: dict[str, dict[str, Any]],
    feeds_by_code: dict[str, dict[str, Any]],
) -> tuple[float, str, dict[str, Any]] | None:
    mapping = next((item for item in COMMODITY_MAPPINGS if item.code == entry["itemCode"]), None)
    if not mapping:
        return None
    complex_entry = cache_by_code.get({
        "PORK": "SEFD",
        "BEEF": "SEFC",
        "POULTRY": "SEFF",
        "DAIRY": "SEFJ",
        "EGGS": "SEFH",
    }[mapping.complex_name])
    feed_status = feeds_by_code.get(entry["itemCode"]) or feeds_by_code.get({
        "PORK": "SEFD",
        "BEEF": "SEFC",
        "POULTRY": "SEFF",
        "DAIRY": "SEFJ",
        "EGGS": "SEFH",
    }[mapping.complex_name])
    own = _history_forecast(entry, target_month)
    pooled = _history_forecast(complex_entry, target_month) if complex_entry else own
    lag_profile = _lag_profile(entry, complex_entry)
    live_adjustment = _live_cut_adjustment(mapping, feed_status)
    pooled_share = 0.35 if safe_std([value for _, value in history_mm(entry, seasonal=False)], 0.0) <= 0.02 else 0.50
    forecast = (1.0 - pooled_share) * own + pooled_share * pooled + lag_profile["loading"] * live_adjustment
    validation = validation_for(mapping, entry)
    model_card = {
        "complex": mapping.complex_name,
        "latentFactor": mapping.latent_factor,
        "mappedCuts": list(mapping.cuts),
        "selectedLag": lag_profile["lag"],
        "estimatedLoading": lag_profile["loading"],
        "lagCorrelation": lag_profile["correlation"],
        "liveCutAdjustment": live_adjustment,
        "validation": validation,
        "decision": "granular_kept_pending_backtest" if validation["apCpiCorrelation"] is None or validation["apCpiCorrelation"] >= -0.25 else "granular_review",
        "notes": mapping.notes,
    }
    driver = (
        f"{mapping.complex_name} commodity-complex factor: cuts {', '.join(mapping.cuts)}; "
        f"lag {lag_profile['lag']}, loading {lag_profile['loading']:.2f}; "
        f"live cut adjustment {live_adjustment * 100:.2f} pp"
    )
    return forecast, driver, model_card


def commodity_backtest_rows(cache_by_code: dict[str, dict[str, Any]], start: str = "2022-01") -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for mapping in COMMODITY_MAPPINGS:
        entry = cache_by_code.get(mapping.code)
        complex_entry = cache_by_code.get({
            "PORK": "SEFD",
            "BEEF": "SEFC",
            "POULTRY": "SEFF",
            "DAIRY": "SEFJ",
            "EGGS": "SEFH",
        }[mapping.complex_name])
        if not entry or not complex_entry:
            continue
        actual = dict(history_mm(entry, seasonal=False))
        granular_errors = []
        composite_errors = []
        months = sorted(month for month in actual if month >= start)
        for month in months:
            y = actual.get(month)
            if y is None:
                continue
            idx = [point["month"] for point in entry["history"]].index(month)
            if idx < 12:
                continue
            prior_entry = {**entry, "history": entry["history"][:idx]}
            prior_complex = {**complex_entry, "history": complex_entry["history"][:idx]}
            own = _history_forecast(prior_entry, month)
            composite = _history_forecast(prior_complex, month)
            granular = 0.65 * own + 0.35 * composite
            granular_errors.append(abs(granular - y))
            composite_errors.append(abs(composite - y))
        with_mae = safe_mean(granular_errors, None) if granular_errors else None
        without_mae = safe_mean(composite_errors, None) if composite_errors else None
        rows.append(
            {
                "itemCode": mapping.code,
                "name": entry["name"],
                "complex": mapping.complex_name,
                "mappedCuts": list(mapping.cuts),
                "withoutGranularMae": without_mae,
                "withGranularMae": with_mae,
                "winner": "granular" if with_mae is not None and without_mae is not None and with_mae <= without_mae else "composite_only",
                "kept": with_mae is not None and without_mae is not None and with_mae <= without_mae,
                "validation": validation_for(mapping, entry),
            }
        )
    return rows


def write_commodity_report(month: str, payload: dict[str, Any], cache_by_code: dict[str, dict[str, Any]]) -> dict[str, Any]:
    rows = commodity_backtest_rows(cache_by_code)
    report = {
        "forecastMonth": month,
        "window": "C",
        "requestedStart": "2022-01",
        "notes": "With-granular uses sub-stratum CPI history partially pooled to the complex factor plus mapped live cut metadata. Wholesale-to-AP validation will activate after the local USDA cut archive has history.",
        "rows": rows,
    }
    run_dir = RUNS_DIR / month
    write_json(run_dir / "food_commodity_complex_backtest.json", report)
    lines = [
        f"# Food commodity-complex backtest: {month}",
        "",
        report["notes"],
        "",
        "| Component | Complex | Cuts | Without granular MAE | With granular MAE | Winner | AP-CPI corr |",
        "|---|---|---|---:|---:|---|---:|",
    ]
    for row in rows:
        validation = row.get("validation") or {}
        lines.append(
            "| {name} | {complex} | {cuts} | {without} | {with_} | {winner} | {corr} |".format(
                name=row["name"].replace("|", "/"),
                complex=row["complex"],
                cuts=", ".join(row["mappedCuts"]).replace("|", "/"),
                without="n/a" if row["withoutGranularMae"] is None else f"{row['withoutGranularMae'] * 100:.2f}%",
                with_="n/a" if row["withGranularMae"] is None else f"{row['withGranularMae'] * 100:.2f}%",
                winner=row["winner"],
                corr="n/a" if validation.get("apCpiCorrelation") is None else f"{validation['apCpiCorrelation']:.2f}",
            )
        )
    (run_dir / "food_commodity_complex_backtest.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report
