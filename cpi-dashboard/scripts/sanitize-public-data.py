from __future__ import annotations

import argparse
import copy
import json
import shutil
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "src" / "data"
PUBLIC_DIR = ROOT / "src" / "data-public"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, allow_nan=False), encoding="utf-8")


def sanitize_extended_registry(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    public = []
    for row in rows:
        public.append(
            {
                **row,
                "model_type": "public_dashboard_summary" if row.get("tier") else row.get("model_type"),
                "input_series": [],
                "pass_through_lags": [],
                "event_calendar": [],
                "stats": {},
            }
        )
    return public


def sanitize_feed_health(payload: dict[str, Any]) -> dict[str, Any]:
    components = []
    for row in payload.get("components", []):
        components.append(
            {
                "itemCode": row.get("itemCode"),
                "name": row.get("name"),
                "tier": row.get("tier"),
                "primaryFeed": "Hidden in public build",
                "secondaryFeeds": [],
                "status": "public_hidden",
                "fallbackUsed": False,
                "lastObservationDate": None,
                "latestValue": None,
                "unit": row.get("unit"),
                "observationsUsed": [],
                "details": "Live-feed diagnostics are available only in the local/private dashboard.",
            }
        )
    return {
        "forecastMonth": payload.get("forecastMonth"),
        "generatedAt": payload.get("generatedAt"),
        "summary": {
            "componentsTracked": len(components),
            "live": 0,
            "partial": 0,
            "fallbackOrBlocked": 0,
        },
        "components": components,
    }


def sanitize_forecast(payload: dict[str, Any]) -> dict[str, Any]:
    public = copy.deepcopy(payload)
    public.pop("foodSubstrataResolution", None)
    public["source"] = "Public dashboard summary; model internals and live-feed diagnostics hidden."
    public["feedHealth"] = {"componentsTracked": 0, "live": 0, "partial": 0, "fallbackOrBlocked": 0}
    for row in public.get("components", []):
        row["modelType"] = "public_nowcast"
        row["driverSnapshot"] = "Public build hides model drivers and feed details."
        row["inputSeries"] = []
        row["passThroughLags"] = []
        row["eventCalendar"] = []
        row["sigma"] = 0
        row.pop("feedStatus", None)
        row.pop("commodityModel", None)
        row.pop("fallback_nsa_mm", None)
        row.pop("fallback_driver", None)
    if public.get("foodForwardPath"):
        public["foodForwardPath"]["note"] = "Public build hides forward-path feature details."
        public["foodForwardPath"]["lagReport"] = {
            "status": "public_hidden",
            "notes": "Feature lag profiles are available only in the local/private dashboard.",
            "rows": [],
        }
        for horizon in public["foodForwardPath"].get("horizons", []):
            for component in horizon.get("components", []):
                component["futuresFeaturesKept"] = False
    return public


def sanitize_diff(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "forecastMonth": payload.get("forecastMonth"),
        "thresholdPp": payload.get("thresholdPp", 0.02),
        "rows": [],
        "note": "Scaffold/live driver diffs are hidden in the public build.",
    }


def sanitize_backtest(payload: dict[str, Any]) -> dict[str, Any]:
    public = copy.deepcopy(payload)
    public["componentLeague"] = [
        {
            "itemCode": row.get("itemCode"),
            "name": row.get("name"),
            "mae": row.get("mae", 0),
            "benchmarkMae": row.get("benchmarkMae", 0),
            "note": "Detailed component diagnostics hidden in public build.",
        }
        for row in public.get("componentLeague", [])
    ]
    if public.get("commodityComplex"):
        public["commodityComplex"] = {
            "window": public["commodityComplex"].get("window"),
            "requestedStart": public["commodityComplex"].get("requestedStart"),
            "notes": "Commodity-complex diagnostics hidden in public build.",
            "rows": [],
        }
    public["diagnostics"] = {"public": "Detailed model diagnostics hidden in public build."}
    return public


def build_public_tree(out_dir: Path) -> None:
    if out_dir.exists():
        shutil.rmtree(out_dir)
    shutil.copytree(DATA_DIR, out_dir)

    write_json(out_dir / "extended-registry.json", sanitize_extended_registry(read_json(DATA_DIR / "extended-registry.json")))
    write_json(out_dir / "forecast" / "latest-forecast.json", sanitize_forecast(read_json(DATA_DIR / "forecast" / "latest-forecast.json")))
    write_json(out_dir / "forecast" / "feed-health.json", sanitize_feed_health(read_json(DATA_DIR / "forecast" / "feed-health.json")))
    write_json(out_dir / "forecast" / "diff-vs-scaffold.json", sanitize_diff(read_json(DATA_DIR / "forecast" / "diff-vs-scaffold.json")))
    for window in ["A", "B", "C"]:
        name = f"backtest-{window}.json"
        write_json(out_dir / "forecast" / name, sanitize_backtest(read_json(DATA_DIR / "forecast" / name)))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--in-place", action="store_true", help="Replace src/data with sanitized public data.")
    args = parser.parse_args()

    if args.in_place:
        tmp = ROOT / ".public-data-tmp"
        build_public_tree(tmp)
        shutil.rmtree(DATA_DIR)
        shutil.move(str(tmp), str(DATA_DIR))
        print("Replaced src/data with sanitized public data.")
    else:
        build_public_tree(PUBLIC_DIR)
        print(f"Wrote {PUBLIC_DIR.relative_to(ROOT)}.")


if __name__ == "__main__":
    main()
