from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from typing import Any

from .commodity_complex import (
    commodity_backtest_rows,
    forecast_commodity_component,
    resolve_food_substrata,
    write_commodity_report,
    write_cut_series,
)
from .data import cache_entries, entry_by_code, history_mm, latest_month, load_dashboard_cache, load_registry, write_json
from .feeds import build_feed_health, feed_health_by_code
from .math import add_months, month_name, normal_interval, pct_change, safe_mean, safe_std
from .paths import RUNS_DIR
from .triage import build_extended_registry
from .used_vehicles import forecast_seta02_sa


def is_core_component(entry: dict[str, Any]) -> bool:
    code = entry["itemCode"]
    name = entry["name"].lower()
    if code.startswith(("SAF", "SEF", "SSF")) or "food" in name or "alcoholic beverage" in name:
        return False
    energy_terms = ("gasoline", "motor fuel", "fuel oil", "electricity", "utility (piped) gas", "energy")
    return not any(term in name for term in energy_terms)


def same_month_values(points: list[tuple[str, float | None]], target_month: str) -> list[float | None]:
    suffix = target_month[-2:]
    return [value for month, value in points if month[-2:] == suffix]


def last_value(points: list[tuple[str, float | None]]) -> float | None:
    for _, value in reversed(points):
        if value is not None:
            return value
    return None


def point_by_month(entry: dict[str, Any], month: str) -> dict[str, Any] | None:
    return next((point for point in entry["history"] if point["month"] == month), None)


def seasonal_adjustment_offset(entry: dict[str, Any], target_month: str) -> float:
    nsa = dict(history_mm(entry, seasonal=False))
    sa = dict(history_mm(entry, seasonal=True))
    offsets = [
        (sa[month] - nsa[month])
        for month in nsa
        if month[-2:] == target_month[-2:] and nsa.get(month) is not None and sa.get(month) is not None
    ]
    return safe_mean(offsets, 0.0)


def forecast_component(entry: dict[str, Any], model: dict[str, Any], target_month: str, feed: dict[str, Any] | None = None) -> tuple[float, str]:
    points = history_mm(entry, seasonal=False)
    values = [value for _, value in points if value is not None]
    last = last_value(points)
    trailing3 = safe_mean(values[-3:], last or 0.0)
    trailing6 = safe_mean(values[-6:], trailing3)
    seasonal = safe_mean(same_month_values(points, target_month), trailing6)
    tier = model.get("tier")
    model_type = model.get("model_type", "")

    if entry["itemCode"] == "SEHB":
        if feed and feed.get("lodgingNsaMm") is not None:
            return float(feed["lodgingNsaMm"]), str(feed.get("lodgingDriver") or "CoStar/STR ADR primary")
        fallback = 0.45 * (last or 0.0) + 0.25 * trailing3 + 0.20 * seasonal + 0.10 * trailing6
        return fallback, "CoStar/STR ADR feed outage; Tier 3 Seasonal AR fallback"

    if entry["itemCode"] == "SETB01" and feed:
        if feed.get("forecastNsaMm") is not None:
            return float(feed["forecastNsaMm"]), str(feed.get("forecastDriver") or "EIA gasoline calendar-month average")
        aaa_obs = [obs for obs in feed.get("observationsUsed", []) if "AAA" in obs.get("label", "")]
        if feed.get("fallbackUsed"):
            live = ""
            if aaa_obs:
                obs = aaa_obs[0]
                live = f"AAA current national regular ${obs['value']:.3f}/gal observed {obs['date']}; "
            return (
                0.55 * (last or 0.0) + 0.30 * trailing3 + 0.15 * seasonal,
                live + "fallback used because EIA calendar-month gasoline feed is unavailable",
            )
    if entry["itemCode"] == "SETG01" and feed and feed.get("jetFuelNsaMm") is not None:
        fallback = 0.55 * (last or 0.0) + 0.30 * trailing3 + 0.15 * seasonal
        jet_move = float(feed["jetFuelNsaMm"])
        pass_through = min(max(0.12 * jet_move, -0.04), 0.04)
        forecast = min(max(fallback + pass_through, -0.08), 0.08)
        return (
            forecast,
            f"airfare fallback {fallback * 100:.2f}% plus guarded jet-fuel pass-through "
            f"{pass_through * 100:.2f}% from {feed.get('jetFuelDriver')}",
        )
    if entry["itemCode"] == "SETA02" and feed:
        used_vehicle_forecast = forecast_seta02_sa(entry, target_month, feed)
        if used_vehicle_forecast:
            sa_forecast, driver = used_vehicle_forecast
            return (
                sa_forecast - seasonal_adjustment_offset(entry, target_month),
                driver + " SA forecast converted to NSA using the component's historical SA/NSA offset.",
            )
    if tier == 1:
        # Free-data fallback: use CPI-consistent timing from recent movement plus same-month seasonality.
        return 0.55 * (last or 0.0) + 0.30 * trailing3 + 0.15 * seasonal, "free fallback: recent CPI-timed movement + same-month seasonal average"
    if tier == 2 and ("shelter" in model_type or "oer" in model_type):
        lagged = values[-18:-5] if len(values) >= 18 else values[-12:]
        cpi_lagged = 0.80 * safe_mean(lagged, trailing6) + 0.20 * trailing6
        if feed and feed.get("shelterMarketNsaMm") is not None:
            market = float(feed["shelterMarketNsaMm"])
            forecast = 0.75 * cpi_lagged + 0.25 * market
            return (
                forecast,
                "75% lagged BLS shelter history "
                f"({cpi_lagged * 100:.2f}%) + 25% lagged external rent overlay "
                f"({market * 100:.2f}%): {feed.get('shelterMarketDriver')}",
            )
        return cpi_lagged, "distributed lag over trailing BLS shelter history fallback"
    if tier == 2 and "tuition" in model_type:
        if target_month[-2:] in {"08", "09"}:
            return max(seasonal, safe_mean(values[-24:], 0.0)), "academic-year event month"
        return min(max(trailing6 * 0.15, -0.0005), 0.0008), "non-event month drift"
    if tier == 2 and "retained_earnings" in model_type:
        if target_month[-2:] in {"04", "10"}:
            return 0.65 * seasonal + 0.35 * trailing6, "scheduled retained-earnings reset fallback"
        return trailing6 * 0.35, "between-reset drift"
    if tier == 4:
        return 0.50 * trailing6 + 0.50 * seasonal, "parent-inherit fallback using class trend/seasonality"

    # Tier 3 statistical partial-pooling approximation.
    return 0.45 * (last or 0.0) + 0.25 * trailing3 + 0.20 * seasonal + 0.10 * trailing6, "seasonal AR partial-pooling fallback"


def tier3_ar_fallback(entry: dict[str, Any], target_month: str) -> tuple[float, str]:
    return forecast_component(entry, {"tier": 3, "model_type": "seasonal_ar_partial_pool"}, target_month, None)


def projection_source_for_row(row: dict[str, Any]) -> str:
    tier = row.get("tier")
    if tier == 4:
        return "parent"
    if tier == 3:
        return "AR fallback"
    return "model"


def log_forecast_error(feed_health: dict[str, Any], entry: dict[str, Any], stage: str, exc: Exception) -> None:
    errors = feed_health.setdefault("forecastErrors", [])
    errors.append(
        {
            "itemCode": entry.get("itemCode"),
            "name": entry.get("name"),
            "stage": stage,
            "errorType": type(exc).__name__,
            "message": str(exc),
        }
    )
    feed_health.setdefault("summary", {})["forecastErrors"] = len(errors)


def aggregate(rows: list[dict[str, Any]], *, core: bool = False) -> tuple[float, list[dict[str, Any]]]:
    selected = [row for row in rows if (row["is_core"] if core else True)]
    denominator = sum(row["model_weight"] for row in selected) if core else 100.0
    if denominator <= 0:
        return 0.0, []
    scaled = []
    total_pp = 0.0
    for row in selected:
        weight = row["model_weight"]
        pp = weight * row["forecast_nsa_mm"]
        total_pp += pp
        scaled.append({**row, "aggregate_weight": weight, "contribution_pp": pp})
    return total_pp / denominator, scaled


def build_food_forward_path(rows: list[dict[str, Any]], feed_health: dict[str, Any]) -> dict[str, Any]:
    food_rows = [
        row
        for row in rows
        if (
            row["model_weight"] > 0
            and (row["itemCode"].startswith("SEF") or row["itemCode"].startswith("SAF") or "food" in row["name"].lower())
            and "away from home" not in row["name"].lower()
        )
    ]
    lag_report = feed_health.get("foodFuturesLagReport") or {}
    futures_active = any(item.get("kept") for item in lag_report.get("rows", []))
    horizons = []
    for horizon in range(1, 7):
        decay = 1.0 if horizon == 1 else max(0.35, 1.0 - 0.10 * (horizon - 1))
        component_rows = []
        contribution_sum = 0.0
        weight_sum = 0.0
        for row in food_rows:
            mm = row["forecast_nsa_mm"] * decay
            contribution = row["model_weight"] * mm
            contribution_sum += contribution
            weight_sum += row["model_weight"]
            component_rows.append(
                {
                    "itemCode": row["itemCode"],
                    "name": row["name"],
                    "nsaMm": mm,
                    "contributionPp": contribution,
                    "interval": {
                        "p10": mm - (0.0015 * horizon),
                        "p50": mm,
                        "p90": mm + (0.0015 * horizon),
                    },
                    "futuresFeaturesKept": futures_active,
                }
            )
        food_nsa = contribution_sum / weight_sum if weight_sum else 0.0
        horizons.append(
            {
                "horizon": horizon,
                "label": f"t+{horizon}",
                "foodNsaMm": food_nsa,
                "headlineContributionPp": contribution_sum,
                "interval": {
                    "p10": food_nsa - (0.0015 * horizon),
                    "p50": food_nsa,
                    "p90": food_nsa + (0.0015 * horizon),
                },
                "components": sorted(component_rows, key=lambda item: abs(item["contributionPp"]), reverse=True)[:12],
            }
        )
    return {
        "status": "futures_active" if futures_active else "no_live_futures_history",
        "source": "model output, not BLS data",
        "note": "USDA food feeds remain primary. CME futures features are additive only where live history improves window-C walk-forward error; none are kept while CME/Stooq endpoints are blocked.",
        "horizons": horizons,
        "lagReport": lag_report,
    }


def implied_yoy(entry: dict[str, Any], target_month: str, forecast_mm: float, *, seasonal: bool = False) -> float | None:
    prior_month = add_months(target_month, -1)
    year_ago = add_months(target_month, -12)
    prior = point_by_month(entry, prior_month)
    base = point_by_month(entry, year_ago)
    index_key = "saIndex" if seasonal else "nsaIndex"
    if not prior or not base or not prior.get(index_key) or not base.get(index_key):
        return None
    forecast_index = prior[index_key] * (1.0 + forecast_mm)
    return forecast_index / base[index_key] - 1.0


def build_projection_components(
    *,
    target_month: str,
    entries: dict[str, dict[str, Any]],
    extended: list[dict[str, Any]],
    rows: list[dict[str, Any]],
    feeds_by_code: dict[str, dict[str, Any]],
    feed_health: dict[str, Any],
) -> list[dict[str, Any]]:
    model_by_code = {entry["item_code"]: entry for entry in extended}
    rows_by_code = {row["itemCode"]: row for row in rows}
    children: dict[str, list[dict[str, Any]]] = {}
    for entry in entries.values():
        parent = entry.get("parent")
        if parent:
            children.setdefault(parent, []).append(entry)

    projections: dict[str, dict[str, Any]] = {}

    def projection_row(
        entry: dict[str, Any],
        nsa_mm: float,
        source: str,
        detail: str,
        *,
        child_count: int = 0,
        display: bool = True,
    ) -> dict[str, Any]:
        sa_mm = nsa_mm + seasonal_adjustment_offset(entry, target_month)
        return {
            "itemCode": entry["itemCode"],
            "name": entry["name"],
            "parent": entry.get("parent"),
            "weight": entry.get("currentRi"),
            "forecast_nsa_mm": nsa_mm,
            "forecast_sa_mm": sa_mm,
            # Projection components feed the heatmap's SA contribution view.
            "contribution_pp": (entry.get("currentRi") or 0.0) * sa_mm,
            "projectionSource": source,
            "projectionSourceDetail": detail,
            "childProjectionCount": child_count,
            "displayInHeatmap": display,
        }

    for code, row in rows_by_code.items():
        entry = entries.get(code)
        if not entry:
            continue
        projections[code] = projection_row(
            entry,
            float(row["forecast_nsa_mm"]),
            projection_source_for_row(row),
            row.get("driverSnapshot") or row.get("modelType") or "direct model projection",
        )

    def standalone_projection(entry: dict[str, Any]) -> dict[str, Any] | None:
        code = entry["itemCode"]
        model = model_by_code.get(code, {"tier": 3, "model_type": "seasonal_ar_partial_pool"})
        if model.get("tier") in {1, 2}:
            try:
                nsa_mm, driver = forecast_component(entry, model, target_month, feeds_by_code.get(code))
                return projection_row(entry, nsa_mm, "model", driver)
            except Exception as exc:  # pragma: no cover - exercised by artifact tests if a real model fails
                log_forecast_error(feed_health, entry, "projection_model", exc)
        try:
            nsa_mm, driver = tier3_ar_fallback(entry, target_month)
            return projection_row(entry, nsa_mm, "AR fallback", driver)
        except Exception as exc:  # pragma: no cover - defensive guard for malformed histories
            log_forecast_error(feed_health, entry, "projection_ar_fallback", exc)
            return None

    def project(code: str, stack: tuple[str, ...] = ()) -> dict[str, Any] | None:
        if code in projections:
            return projections[code]
        if code in stack:
            return None
        entry = entries.get(code)
        if not entry or not entry.get("history"):
            return None

        child_rows = [project(child["itemCode"], stack + (code,)) for child in children.get(code, [])]
        usable_children = [
            child
            for child in child_rows
            if child and child.get("weight") is not None and child.get("forecast_nsa_mm") is not None
        ]
        child_weight = sum(float(child["weight"] or 0.0) for child in usable_children)
        if usable_children and child_weight > 0:
            nsa_mm = sum(float(child["weight"] or 0.0) * float(child["forecast_nsa_mm"]) for child in usable_children) / child_weight
            projections[code] = projection_row(
                entry,
                nsa_mm,
                "aggregate",
                f"weighted sum of {len(usable_children)} child projections",
                child_count=len(usable_children),
                display=code != "SEHC01",
            )
            return projections[code]

        standalone = standalone_projection(entry)
        if standalone:
            standalone["displayInHeatmap"] = code != "SEHC01"
            projections[code] = standalone
            return standalone

        parent = entry.get("parent")
        parent_projection = project(parent, stack + (code,)) if parent else None
        if parent_projection and parent_projection.get("forecast_nsa_mm") is not None:
            projections[code] = projection_row(
                entry,
                float(parent_projection["forecast_nsa_mm"]),
                "parent",
                f"inherited from {parent}",
                display=code != "SEHC01",
            )
            return projections[code]
        return None

    for code in entries:
        project(code)
    return sorted(projections.values(), key=lambda row: (row.get("weight") is not None, row.get("weight") or -1), reverse=True)


def build_forecast(month: str) -> dict[str, Any]:
    extended = build_extended_registry()
    model_by_code = {entry["item_code"]: entry for entry in extended}
    cache_by_code = entry_by_code()
    feed_health = build_feed_health(month)
    write_cut_series(feed_health)
    food_substrata_resolution = resolve_food_substrata(cache_by_code)
    commodity_decisions = {row["itemCode"]: row for row in commodity_backtest_rows(cache_by_code, start="2022-01")}
    feeds_by_code = feed_health_by_code(feed_health)
    if feed_health.get("derived", {}).get("gasolineEiaNsaMm") is not None and "SETB01" in feeds_by_code:
        feeds_by_code["SETB01"]["forecastNsaMm"] = feed_health["derived"]["gasolineEiaNsaMm"]
        feeds_by_code["SETB01"]["forecastDriver"] = feed_health["derived"].get("gasolineEiaDriver")
    if feed_health.get("derived", {}).get("jetFuelEiaNsaMm") is not None and "SETG01" in feeds_by_code:
        feeds_by_code["SETG01"]["jetFuelNsaMm"] = feed_health["derived"]["jetFuelEiaNsaMm"]
        feeds_by_code["SETG01"]["jetFuelDriver"] = feed_health["derived"].get("jetFuelEiaDriver")
    rows: list[dict[str, Any]] = []
    for model in extended:
        if model.get("model_weight") is None:
            continue
        entry = cache_by_code.get(model["item_code"])
        if not entry:
            continue
        try:
            commodity_forecast = forecast_commodity_component(entry, month, cache_by_code, feeds_by_code)
            if commodity_forecast:
                forecast, driver, commodity_model = commodity_forecast
            else:
                forecast, driver = forecast_component(entry, model, month, feeds_by_code.get(entry["itemCode"]))
                commodity_model = None
            fallback_forecast, fallback_driver = forecast_component(entry, model, month, None)
        except Exception as exc:
            log_forecast_error(feed_health, entry, "component_forecast", exc)
            forecast, driver = tier3_ar_fallback(entry, month)
            fallback_forecast, fallback_driver = forecast, driver
            commodity_model = None
            driver = f"forecast error fell back to AR fallback: {type(exc).__name__}: {exc}; {driver}"
        if commodity_model:
            decision = commodity_decisions.get(entry["itemCode"])
            commodity_model["windowC"] = decision
            if not (decision and decision.get("kept")):
                forecast = fallback_forecast
                commodity_model["decision"] = "granular_dropped_window_c"
                driver = (
                    "Commodity-complex mapping documented but dropped because it did not improve window-C error; "
                    f"using prior fallback. Candidate cuts: {', '.join(commodity_model.get('mappedCuts') or [])}"
                )
            else:
                commodity_model["decision"] = "granular_kept_window_c"
        forecast_sa = forecast + seasonal_adjustment_offset(entry, month)
        rows.append(
            {
                "itemCode": entry["itemCode"],
                "name": entry["name"],
                "tier": model.get("tier"),
                "modelType": model.get("model_type"),
                "model_weight": float(model.get("model_weight") or 0.0),
                "blsCurrentRi": entry.get("currentRi"),
                "forecast_nsa_mm": forecast,
                "forecast_sa_mm": forecast_sa,
                "fallback_nsa_mm": fallback_forecast,
                "fallback_driver": fallback_driver,
                "is_core": is_core_component(entry),
                "driverSnapshot": driver,
                "feedStatus": feeds_by_code.get(entry["itemCode"]),
                "inputSeries": model.get("input_series", []),
                "passThroughLags": model.get("pass_through_lags", []),
                "eventCalendar": model.get("event_calendar", []),
                "sigma": float((model.get("stats") or {}).get("sigma") or 0.0),
                "component_yoy": implied_yoy(entry, month, forecast),
                "commodityModel": commodity_model,
            }
        )

    headline_nsa, headline_rows = aggregate(rows)
    core_nsa, core_rows = aggregate(rows, core=True)
    headline_sa = headline_nsa + seasonal_adjustment_offset(cache_by_code["SA0"], month)
    core_sa = core_nsa + seasonal_adjustment_offset(cache_by_code["SA0L1E"], month)

    for row in rows:
        # contribution to headline in percentage points: RI_i,t-1 * r_i,t
        row["contribution_pp"] = row["model_weight"] * row["forecast_nsa_mm"]

    projection_components = build_projection_components(
        target_month=month,
        entries=cache_by_code,
        extended=extended,
        rows=rows,
        feeds_by_code=feeds_by_code,
        feed_health=feed_health,
    )

    headline_entry = cache_by_code["SA0"]
    core_entry = cache_by_code["SA0L1E"]
    headline_sigma = (sum((row["model_weight"] / 100.0 * row["sigma"]) ** 2 for row in rows) ** 0.5) or 0.0015
    core_denominator = sum(row["aggregate_weight"] for row in core_rows) or 100.0
    core_sigma = (sum((row["aggregate_weight"] / core_denominator * row["sigma"]) ** 2 for row in core_rows) ** 0.5) or 0.0012
    h_interval = normal_interval(headline_sa, headline_sigma)
    c_interval = normal_interval(core_sa, core_sigma)

    base_effects = []
    for offset in range(6):
        scenario_month = add_months(month, offset)
        for scenario in [0.0, 0.002, 0.003]:
            base_effects.append(
                {
                    "month": scenario_month,
                    "scenario_mm": scenario,
                    "headline_yoy": implied_yoy(headline_entry, scenario_month, scenario),
                }
            )

    payload = {
        "forecastMonth": month,
        "generatedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "dataThrough": latest_month(),
        "source": "model output, not BLS data",
        "headline": {
            "nsaMm": headline_nsa,
            "saMm": headline_sa,
            "nsaYoy": implied_yoy(headline_entry, month, headline_nsa),
            "saYoy": implied_yoy(headline_entry, month, headline_sa, seasonal=True),
            "saInterval": h_interval.__dict__,
        },
        "core": {
            "nsaMm": core_nsa,
            "saMm": core_sa,
            "nsaYoy": implied_yoy(core_entry, month, core_nsa),
            "saYoy": implied_yoy(core_entry, month, core_sa, seasonal=True),
            "saInterval": c_interval.__dict__,
        },
        "baseEffects": base_effects,
        "feedHealth": feed_health["summary"],
        "foodSubstrataResolution": food_substrata_resolution,
        "components": sorted(rows, key=lambda row: abs(row["contribution_pp"]), reverse=True),
        "projectionComponents": projection_components,
    }
    payload["foodForwardPath"] = build_food_forward_path(rows, feed_health)
    return payload


def write_diff_report(payload: dict[str, Any]) -> None:
    run_dir = RUNS_DIR / payload["forecastMonth"]
    rows = []
    for row in payload["components"]:
        fallback = row.get("fallback_nsa_mm")
        if fallback is None:
            continue
        delta_mm = row["forecast_nsa_mm"] - fallback
        delta_pp = row["model_weight"] * delta_mm
        rows.append({**row, "delta_mm": delta_mm, "delta_contribution_pp": delta_pp})
    rows = sorted(rows, key=lambda item: abs(item["delta_contribution_pp"]), reverse=True)
    write_json(
        run_dir / "diff_vs_scaffold.json",
        {
            "forecastMonth": payload["forecastMonth"],
            "thresholdPp": 0.02,
            "rows": [
                {
                    "itemCode": row["itemCode"],
                    "name": row["name"],
                    "modelWeight": row["model_weight"],
                    "liveNsaMm": row["forecast_nsa_mm"],
                    "scaffoldNsaMm": row["fallback_nsa_mm"],
                    "deltaContributionPp": row["delta_contribution_pp"],
                    "flagged": abs(row["delta_contribution_pp"]) > 0.02,
                    "liveDriver": row["driverSnapshot"],
                    "scaffoldDriver": row["fallback_driver"],
                }
                for row in rows
            ],
        },
    )
    lines = [
        f"# Diff vs scaffold: {month_name(payload['forecastMonth'])}",
        "",
        "Positive delta means the live-feed version adds more to headline than the scaffold fallback.",
        "",
        "| Component | Live NSA m/m | Scaffold NSA m/m | Delta contribution | Flag | Driver |",
        "|---|---:|---:|---:|---|---|",
    ]
    for row in rows[:80]:
        lines.append(
            "| {name} | {live:.2f}% | {fallback:.2f}% | {delta:.3f} pp | {flag} | {driver} |".format(
                name=str(row["name"]).replace("|", "/"),
                live=row["forecast_nsa_mm"] * 100,
                fallback=row["fallback_nsa_mm"] * 100,
                delta=row["delta_contribution_pp"],
                flag="yes" if abs(row["delta_contribution_pp"]) > 0.02 else "",
                driver=str(row["driverSnapshot"]).replace("|", "/"),
            )
        )
    (run_dir / "diff_vs_scaffold.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_food_futures_report(payload: dict[str, Any]) -> None:
    run_dir = RUNS_DIR / payload["forecastMonth"]
    forward = payload.get("foodForwardPath") or {}
    lag_report = forward.get("lagReport") or {}
    write_json(run_dir / "food_futures_backtest.json", lag_report)
    lines = [
        f"# Food futures with/without report: {month_name(payload['forecastMonth'])}",
        "",
        "Model output, not BLS data.",
        "",
        lag_report.get("notes", "No lag report available."),
        "",
        "| Component | Features | Available | Decision | Expected lag peak | Without futures MAE | With futures MAE | Winner |",
        "|---|---|---|---|---|---:|---:|---|",
    ]
    for row in lag_report.get("rows", []):
        window = row.get("windowC") or {}
        lines.append(
            "| {component} | {features} | {available} | {decision} | {peak} | {without} | {with_} | {winner} |".format(
                component=row.get("component"),
                features=", ".join(row.get("features") or []),
                available=", ".join(row.get("availableFeatures") or []) or "none",
                decision=row.get("decision"),
                peak=row.get("expectedLagPeak"),
                without="n/a" if window.get("withoutFuturesMae") is None else f"{window['withoutFuturesMae']:.4f}",
                with_="n/a" if window.get("withFuturesMae") is None else f"{window['withFuturesMae']:.4f}",
                winner=window.get("winner"),
            )
        )
    (run_dir / "food_futures_backtest.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_food_diff_report(payload: dict[str, Any]) -> None:
    run_dir = RUNS_DIR / payload["forecastMonth"]
    rows = []
    for row in payload["components"]:
        if not row.get("commodityModel"):
            continue
        delta = row["model_weight"] * (row["forecast_nsa_mm"] - row["fallback_nsa_mm"])
        rows.append({**row, "deltaContributionPp": delta})
    rows = sorted(rows, key=lambda item: abs(item["deltaContributionPp"]), reverse=True)
    write_json(
        run_dir / "food_commodity_diff.json",
        {
            "forecastMonth": payload["forecastMonth"],
            "thresholdPp": 0.02,
            "rows": [
                {
                    "itemCode": row["itemCode"],
                    "name": row["name"],
                    "modelWeight": row["model_weight"],
                    "commodityForecastNsaMm": row["forecast_nsa_mm"],
                    "priorCompositeOnlyNsaMm": row["fallback_nsa_mm"],
                    "deltaContributionPp": row["deltaContributionPp"],
                    "flagged": abs(row["deltaContributionPp"]) > 0.02,
                    "commodityModel": row["commodityModel"],
                }
                for row in rows
            ],
        },
    )
    lines = [
        f"# Food commodity-complex diff: {month_name(payload['forecastMonth'])}",
        "",
        "Flag threshold: absolute move greater than 0.02 percentage point of headline.",
        "",
        "| Component | Commodity model NSA m/m | Prior model NSA m/m | Delta contribution | Flag | Cuts |",
        "|---|---:|---:|---:|---|---|",
    ]
    for row in rows:
        model = row.get("commodityModel") or {}
        lines.append(
            "| {name} | {live:.2f}% | {prior:.2f}% | {delta:.3f} pp | {flag} | {cuts} |".format(
                name=str(row["name"]).replace("|", "/"),
                live=row["forecast_nsa_mm"] * 100,
                prior=row["fallback_nsa_mm"] * 100,
                delta=row["deltaContributionPp"],
                flag="yes" if abs(row["deltaContributionPp"]) > 0.02 else "",
                cuts=", ".join(model.get("mappedCuts") or []).replace("|", "/"),
            )
        )
    (run_dir / "food_commodity_diff.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_markdown(payload: dict[str, Any]) -> None:
    run_dir = RUNS_DIR / payload["forecastMonth"]
    lines = [
        f"# CPI Forecast: {month_name(payload['forecastMonth'])}",
        "",
        "Model output, not BLS data.",
        "",
        f"- Headline NSA m/m: {payload['headline']['nsaMm'] * 100:.2f}%",
        f"- Headline SA m/m: {payload['headline']['saMm'] * 100:.2f}% (P10/P50/P90: {payload['headline']['saInterval']['p10'] * 100:.2f} / {payload['headline']['saInterval']['p50'] * 100:.2f} / {payload['headline']['saInterval']['p90'] * 100:.2f})",
        f"- Core SA m/m: {payload['core']['saMm'] * 100:.2f}%",
        "",
        "| Component | Tier | Model | Weight | NSA m/m | Contribution pp | Driver |",
        "|---|---:|---|---:|---:|---:|---|",
    ]
    for row in payload["components"][:80]:
        lines.append(
            f"| {row['name']} | {row['tier']} | {row['modelType']} | {row['model_weight']:.3f} | {row['forecast_nsa_mm'] * 100:.2f}% | {row['contribution_pp']:.3f} | {row['driverSnapshot']} |"
        )
    (run_dir / "forecast.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--month", default=None, help="Forecast month YYYY-MM. Defaults to next unpublished month.")
    args = parser.parse_args()
    month = args.month or add_months(latest_month(), 1)
    payload = build_forecast(month)
    run_dir = RUNS_DIR / month
    feed_health = build_feed_health(month, write_snapshots=True)
    write_json(run_dir / "forecast.json", payload)
    write_json(run_dir / "input_snapshot.json", {"dashboard_cache_ref_month": latest_month(), "registry_rows": len(load_registry())})
    write_markdown(payload)
    write_diff_report(payload)
    write_food_futures_report(payload)
    write_commodity_report(month, payload, entry_by_code())
    write_food_diff_report(payload)
    from .archive import export_month

    archive_run = export_month(month)
    print(f"Wrote {run_dir / 'forecast.json'}")
    print(f"Wrote archive run {archive_run}")


if __name__ == "__main__":
    main()
