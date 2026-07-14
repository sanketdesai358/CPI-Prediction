from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .data import entry_by_code, write_json
from .math import add_months, pct_change
from .paths import RUNS_DIR


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--month", required=True)
    args = parser.parse_args()
    run_dir = RUNS_DIR / args.month
    forecast_path = run_dir / "forecast.json"
    if not forecast_path.exists():
        raise SystemExit(f"Missing forecast: {forecast_path}")
    forecast = json.loads(forecast_path.read_text(encoding="utf-8"))
    headline = entry_by_code()["SA0"]
    actual = next((point for point in headline["history"] if point["month"] == args.month), None)
    if not actual:
        payload = {"month": args.month, "status": "actual_not_available", "rows": []}
        write_json(run_dir / "score.json", payload)
        print(f"Actual CPI data for {args.month} is not in the cache yet.")
        return
    prior = next((point for point in headline["history"] if point["month"] == add_months(args.month, -1)), None)
    actual_nsa = pct_change(actual.get("nsaIndex"), prior.get("nsaIndex") if prior else None)
    actual_sa = actual.get("saMm")
    entries = entry_by_code()
    rows = []
    for component in forecast["components"]:
        entry = entries.get(component["itemCode"])
        component_actual = next(
            (point for point in (entry or {}).get("history", []) if point["month"] == args.month),
            None,
        )
        prior_component = next(
            (
                point
                for point in (entry or {}).get("history", [])
                if point["month"] == add_months(args.month, -1)
            ),
            None,
        )
        actual_component_nsa = pct_change(
            component_actual.get("nsaIndex") if component_actual else None,
            prior_component.get("nsaIndex") if prior_component else None,
        )
        actual_component_sa = component_actual.get("saMm") if component_actual else None
        weight = component.get("blsCurrentRi") or component.get("model_weight")
        # Score contribution errors on the same SA basis shown by the dashboard.
        # The forecast artifact's legacy contribution_pp can be NSA-based.
        forecast_contribution = (
            None
            if weight is None or component.get("forecast_sa_mm") is None
            else weight * component["forecast_sa_mm"]
        )
        actual_contribution = None if weight is None or actual_component_sa is None else weight * actual_component_sa
        contribution_error = (
            None
            if forecast_contribution is None or actual_contribution is None
            else forecast_contribution - actual_contribution
        )
        feed_status = component.get("feedStatus") or {}
        rows.append(
            {
                "itemCode": component["itemCode"],
                "name": component["name"],
                "tier": component.get("tier"),
                "modelType": component.get("modelType"),
                "weightRi": weight,
                "forecastNsaMm": component.get("forecast_nsa_mm"),
                "actualNsaMm": actual_component_nsa,
                "forecastSaMm": component.get("forecast_sa_mm"),
                "actualSaMm": actual_component_sa,
                "forecastContributionPp": forecast_contribution,
                "actualContributionPp": actual_contribution,
                "contributionErrorPp": contribution_error,
                "missPp": contribution_error,
                "fallbackUsed": bool(feed_status.get("fallbackUsed")),
                "feedStatus": feed_status.get("status"),
                "driverSnapshot": component.get("driverSnapshot"),
            }
        )
    rows.sort(key=lambda row: abs(row["contributionErrorPp"] or 0.0), reverse=True)
    scored_rows = [row for row in rows if row["contributionErrorPp"] is not None]
    actual_headline_yoy = None
    actual_headline_sa_yoy = None
    year_ago = next((point for point in headline["history"] if point["month"] == add_months(args.month, -12)), None)
    if actual and year_ago and actual.get("nsaIndex") and year_ago.get("nsaIndex"):
        actual_headline_yoy = actual["nsaIndex"] / year_ago["nsaIndex"] - 1.0
    if actual and year_ago and actual.get("saIndex") and year_ago.get("saIndex"):
        actual_headline_sa_yoy = actual["saIndex"] / year_ago["saIndex"] - 1.0
    core_entry = entries.get("SA0L1E")
    core_actual = next(
        (point for point in (core_entry or {}).get("history", []) if point["month"] == args.month),
        None,
    )
    core_prior = next(
        (
            point
            for point in (core_entry or {}).get("history", [])
            if point["month"] == add_months(args.month, -1)
        ),
        None,
    )
    core_actual_nsa = pct_change(
        core_actual.get("nsaIndex") if core_actual else None,
        core_prior.get("nsaIndex") if core_prior else None,
    )
    core_actual_sa = core_actual.get("saMm") if core_actual else None
    core_year_ago = next(
        (
            point
            for point in (core_entry or {}).get("history", [])
            if point["month"] == add_months(args.month, -12)
        ),
        None,
    )
    core_actual_yoy = None
    if core_actual and core_year_ago and core_actual.get("nsaIndex") and core_year_ago.get("nsaIndex"):
        core_actual_yoy = core_actual["nsaIndex"] / core_year_ago["nsaIndex"] - 1.0
    payload = {
        "month": args.month,
        "status": "scored" if actual_nsa is not None else "actual_missing",
        "headline": {
            "forecastNsaMm": forecast["headline"]["nsaMm"],
            "actualNsaMm": actual_nsa,
            "forecastSaMm": forecast["headline"]["saMm"],
            "actualSaMm": actual_sa,
            "missSaPp": None if actual_sa is None else 100.0 * (forecast["headline"]["saMm"] - actual_sa),
            "forecastSaYoy": forecast["headline"].get("saYoy"),
            "forecastNsaYoy": forecast["headline"].get("nsaYoy"),
            "actualSaYoy": actual_headline_sa_yoy,
            "actualNsaYoy": actual_headline_yoy,
        },
        "core": {
            "forecastNsaMm": forecast["core"]["nsaMm"],
            "actualNsaMm": core_actual_nsa,
            "forecastSaMm": forecast["core"]["saMm"],
            "actualSaMm": core_actual_sa,
            "forecastSaYoy": forecast["core"].get("saYoy"),
            "forecastNsaYoy": forecast["core"].get("nsaYoy"),
            "actualSaYoy": None if not core_actual or not core_year_ago or not core_actual.get("saIndex") or not core_year_ago.get("saIndex") else core_actual["saIndex"] / core_year_ago["saIndex"] - 1.0,
            "actualNsaYoy": core_actual_yoy,
        },
        "rows": rows,
        "summary": {
            "componentCount": len(rows),
            "scoredComponentCount": len(scored_rows),
            "missingActualCount": len(rows) - len(scored_rows),
            "fallbackCount": sum(1 for row in rows if row["fallbackUsed"]),
            "liveFeedCount": sum(1 for row in rows if row["feedStatus"] == "live" and not row["fallbackUsed"]),
            "topContributionErrors": scored_rows[:10],
        },
    }
    write_json(run_dir / "score.json", payload)
    print(f"Wrote {run_dir / 'score.json'}")


if __name__ == "__main__":
    main()
