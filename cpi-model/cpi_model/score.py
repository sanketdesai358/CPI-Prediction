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
    rows = []
    for component in forecast["components"]:
        rows.append(
            {
                "itemCode": component["itemCode"],
                "name": component["name"],
                "forecastContribution": component["contribution_pp"],
                "actualContribution": None,
                "missPp": None,
            }
        )
    payload = {
        "month": args.month,
        "status": "scored" if actual_nsa is not None else "actual_missing",
        "headline": {
            "forecastNsaMm": forecast["headline"]["nsaMm"],
            "actualNsaMm": actual_nsa,
            "forecastSaMm": forecast["headline"]["saMm"],
            "actualSaMm": actual_sa,
            "missSaPp": None if actual_sa is None else 100.0 * (forecast["headline"]["saMm"] - actual_sa),
        },
        "rows": rows,
    }
    write_json(run_dir / "score.json", payload)
    print(f"Wrote {run_dir / 'score.json'}")


if __name__ == "__main__":
    main()
