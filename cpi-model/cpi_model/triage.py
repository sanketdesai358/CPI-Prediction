from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .data import cache_entries, current_model_components, forecast_universe_codes, history_mm, load_registry, write_json
from .math import ar1, safe_std, seasonal_strength
from .paths import EXTENDED_REGISTRY_PATH, TRIAGE_REPORT_PATH


TIER1: dict[str, dict[str, Any]] = {
    "SETB01": {"model_type": "measurement_pass_through_gasoline", "input_series": ["EIA weekly retail gasoline", "AAA daily gasoline fallback"], "pass_through_lags": [0], "event_calendar": []},
    "SEHE01": {"model_type": "measurement_pass_through_fuel_oil", "input_series": ["EIA heating oil retail"], "pass_through_lags": [0, 1], "event_calendar": ["winter-demand-overlay"]},
    "SEHF02": {"model_type": "distributed_lag_utility_gas", "input_series": ["Henry Hub", "EIA retail natural gas"], "pass_through_lags": [1, 2, 3], "event_calendar": ["tariff-filings"]},
    "SEHF01": {"model_type": "tariff_event_electricity", "input_series": ["EIA retail electricity", "state tariff filings"], "pass_through_lags": [0, 1], "event_calendar": ["tariff-filings"]},
    "SEHA": {"model_type": "shelter_tier1_cpi_fallback", "input_series": ["CPI rent history"], "pass_through_lags": [], "event_calendar": ["six-panel-rotation"]},
    "SEHC": {"model_type": "oer_tier1_cpi_fallback", "input_series": ["CPI OER history"], "pass_through_lags": [], "event_calendar": ["owner-stock-reweighting"]},
    "SEHC01": {"model_type": "oer_tier1_cpi_fallback", "input_series": ["CPI OER history"], "pass_through_lags": [], "event_calendar": ["owner-stock-reweighting"]},
    "SETA02": {"model_type": "used_vehicle_lag_kernel", "input_series": ["Manheim UVVI SA", "Black Book fallback"], "pass_through_lags": [0, 2], "event_calendar": ["Manheim final timing guard", "retail-wholesale level-gap guard"]},
    "SETA01": {"model_type": "new_vehicle_transaction_proxy", "input_series": ["J.D. Power PIN if licensed", "Cox/KBB ATP fallback"], "pass_through_lags": [0, 1], "event_calendar": ["model-year-changeover"]},
    "SETG01": {"model_type": "airfare_fare_mix_proxy", "input_series": ["web fare scrape fallback", "jet fuel", "capacity"], "pass_through_lags": [0, 1], "event_calendar": ["holiday-travel"]},
    "SETA04": {"model_type": "rental_rate_scrape_proxy", "input_series": ["daily rental-rate scrape fallback"], "pass_through_lags": [0], "event_calendar": []},
}

FOOD_INPUT_CODES = {
    "SEFH",
    "SEFC01",
    "SEFC02",
    "SEFC03",
    "SEFC04",
    "SEFD01",
    "SEFD02",
    "SEFD03",
    "SEFD04",
    "SEFF01",
    "SEFF02",
    "SEFJ01",
    "SEFJ02",
    "SEFJ03",
    "SEFJ04",
    "SEFS01",
    "SEFP01",
    "SEFA02",
    "SEFA03",
}

TIER2: dict[str, dict[str, Any]] = {
    "SEME": {"model_type": "health_insurance_retained_earnings_step", "input_series": ["NAIC industry reports", "DMHC commercial insurance"], "pass_through_lags": [10], "event_calendar": ["April retained-earnings update", "October retained-earnings update"]},
    "SEEB01": {"model_type": "tuition_aug_sep_event", "input_series": ["announced tuition data fallback"], "pass_through_lags": [0], "event_calendar": ["August academic-year reset", "September academic-year reset"]},
    "SETE": {"model_type": "insurance_filing_momentum", "input_series": ["rate-filing tracker if licensed", "AR fallback"], "pass_through_lags": [0, 1, 2], "event_calendar": ["filing-effective-dates"]},
    "SEHG": {"model_type": "municipal_fee_calendar_step", "input_series": ["municipal fee schedules"], "pass_through_lags": [0], "event_calendar": ["January reset", "July reset"]},
    "SEED03": {"model_type": "wireless_plan_launch_event", "input_series": ["plan-offer scrape fallback"], "pass_through_lags": [0], "event_calendar": ["plan-launch-events"]},
}


def stats_for(entry: dict[str, Any]) -> dict[str, float | None]:
    points = history_mm(entry)
    values = [value for _, value in points]
    return {
        "weight": entry.get("currentRi"),
        "sigma": safe_std(values),
        "rho": ar1(values),
        "seasonal_strength": seasonal_strength(points),
    }


def default_assignment(entry: dict[str, Any], stats: dict[str, float | None]) -> dict[str, Any]:
    code = entry["itemCode"]
    if code in TIER1:
        return {"tier": 1, **TIER1[code]}
    if code in FOOD_INPUT_CODES or (entry.get("parent") == "SAF11" and (stats.get("weight") or 0) > 0.1):
        return {
            "tier": 1,
            "model_type": "food_commodity_complex_factor",
            "input_series": ["USDA granular cut/feed", "BLS average-price validator", "CPI complex latent factor"],
            "pass_through_lags": [0, 1, 2, 3],
            "event_calendar": ["commodity-complex-pass-through"],
        }
    if code in TIER2:
        return {"tier": 2, **TIER2[code]}
    if entry.get("formula") == "6MR":
        return {
            "tier": 2,
            "model_type": "shelter_six_month_relative",
            "input_series": ["market-rent latent factor fallback"],
            "pass_through_lags": list(range(6, 19)),
            "event_calendar": ["six-panel-rotation"],
        }
    weight = float(stats.get("weight") or 0.0)
    rho = abs(float(stats.get("rho") or 0.0))
    seasonal = float(stats.get("seasonal_strength") or 0.0)
    if weight < 0.1 or (rho < 0.05 and seasonal < 0.05):
        return {"tier": 4, "model_type": "parent_inherit", "input_series": [], "pass_through_lags": [], "event_calendar": []}
    model_type = "seasonal_ar_partial_pool" if rho >= 0.20 else "sarima_partial_pool" if seasonal >= 0.12 else "ets_partial_pool"
    return {"tier": 3, "model_type": model_type, "input_series": [], "pass_through_lags": [], "event_calendar": []}


def build_extended_registry() -> list[dict[str, Any]]:
    cache_by_code = {entry["itemCode"]: entry for entry in cache_entries()}
    registry = load_registry()
    model_units = {entry["itemCode"] for entry in current_model_components()}
    extended: list[dict[str, Any]] = []
    for item in registry:
        code = item["item_code"]
        cache_entry = cache_by_code.get(code)
        if not cache_entry:
            extended.append({**item, "tier": None, "model_type": "unmodeled_missing_history", "input_series": [], "pass_through_lags": [], "event_calendar": [], "stats": {}})
            continue
        stats = stats_for(cache_entry)
        assignment = default_assignment(cache_entry, stats)
        model_weight = None
        if code in model_units:
            model_weight = float(cache_entry.get("currentRi") or 0.0)
        extended.append(
            {
                **item,
                "tier": assignment["tier"],
                "model_type": assignment["model_type"],
                "input_series": assignment["input_series"],
                "pass_through_lags": assignment["pass_through_lags"],
                "event_calendar": assignment["event_calendar"],
                "stats": stats,
                "model_weight": model_weight,
                "bls_current_ri": cache_entry.get("currentRi"),
            }
        )
    return extended


def write_report(extended: list[dict[str, Any]], path: Path = TRIAGE_REPORT_PATH) -> None:
    rows = sorted(extended, key=lambda item: ((item.get("tier") or 9), item.get("item_code", "")))
    lines = [
        "# CPI Model Triage Report",
        "",
        "Generated from the validated registry plus the current BLS history cache. `model_weight` is the BLS current relative-importance weight for the selected non-overlapping forecast universe; parents and overlapping aggregates are excluded from the contribution table.",
        "",
        "| Code | Component | Tier | Model | BLS RI | Model weight | sigma | rho | seasonal |",
        "|---|---|---:|---|---:|---:|---:|---:|---:|",
    ]
    for item in rows:
        stats = item.get("stats") or {}
        lines.append(
            "| {code} | {name} | {tier} | {model} | {ri:.3f} | {mw:.3f} | {sigma:.4f} | {rho:.3f} | {seasonal:.3f} |".format(
                code=item.get("item_code", ""),
                name=str(item.get("name", "")).replace("|", "/"),
                tier=item.get("tier") if item.get("tier") is not None else "",
                model=item.get("model_type", ""),
                ri=float(item.get("bls_current_ri") or 0.0),
                mw=float(item.get("model_weight") or 0.0),
                sigma=float(stats.get("sigma") or 0.0),
                rho=float(stats.get("rho") or 0.0),
                seasonal=float(stats.get("seasonal_strength") or 0.0),
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true", help="Regenerate extended registry and report.")
    args = parser.parse_args()
    extended = build_extended_registry()
    write_json(EXTENDED_REGISTRY_PATH, extended)
    write_report(extended)
    print(f"Wrote {EXTENDED_REGISTRY_PATH.name} with {len(extended)} rows.")
    print(f"Wrote {TRIAGE_REPORT_PATH.name}.")


if __name__ == "__main__":
    main()
