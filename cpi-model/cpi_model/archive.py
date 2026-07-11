from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from .data import entry_by_code, forecast_universe_codes, history_mm, latest_month
from .math import add_months, safe_mean
from .paths import DASHBOARD_ROOT, ROOT as MODEL_ROOT, RUNS_DIR


ARCHIVE_SCHEMA_VERSION = "1.0"
MODELS = {
    "production": "Production",
    "hrnn": "HRNN",
    "i_gru": "I-GRU",
    "seasonal_ar": "Seasonal AR",
}
CHALLENGER_FIELD = {
    "production": "production",
    "hrnn": "hrnn",
    "i_gru": "iGru",
    "seasonal_ar": "seasonalAr",
}
SECRET_PATTERNS = [
    re.compile(r"(api[_-]?key|secret|token|password)\s*[:=]", re.IGNORECASE),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
]


def repo_root() -> Path:
    return MODEL_ROOT.parent


def archive_root() -> Path:
    return repo_root() / "cpi-model-archive"


def dashboard_forecast_path() -> Path:
    return DASHBOARD_ROOT / "src" / "data" / "forecast" / "latest-forecast.json"


def challenger_path() -> Path:
    return MODEL_ROOT / "challenger" / "hrnn" / "results.json"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, allow_nan=False), encoding="utf-8")


def stable_hash(value: Any) -> str:
    blob = json.dumps(value, sort_keys=True, default=str, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()[:16]


def file_hash(path: Path) -> str | None:
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def source_git_sha() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root(),
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()
    except Exception:
        return None


def ensure_archive_repo() -> None:
    root = archive_root()
    root.mkdir(parents=True, exist_ok=True)
    if not (root / ".git").exists():
        subprocess.run(["git", "init"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "CPI Archive Bot"], cwd=root, check=False)
    subprocess.run(["git", "config", "user.email", "cpi-archive@example.local"], cwd=root, check=False)


def choose_run_id(month: str) -> str:
    runs = archive_root() / "runs"
    base = runs / month
    if not base.exists():
        return month
    revision = 2
    while (runs / f"{month}_rev{revision}").exists():
        revision += 1
    return f"{month}_rev{revision}"


def month_from_run_id(run_id: str) -> str:
    return run_id.split("_rev", 1)[0]


def current_components() -> list[dict[str, Any]]:
    by_code = entry_by_code()
    codes = forecast_universe_codes(list(by_code.values()))
    out = []
    for code in codes:
        entry = by_code.get(code)
        if entry and entry.get("currentRi") is not None and entry.get("history"):
            out.append(entry)
    return out


def seasonal_offset(entry: dict[str, Any], month: str) -> float | None:
    nsa = dict(history_mm(entry, seasonal=False))
    sa = dict(history_mm(entry, seasonal=True))
    offsets = [
        sa[m] - nsa[m]
        for m in nsa
        if m < month and m[-2:] == month[-2:] and nsa.get(m) is not None and sa.get(m) is not None
    ]
    return safe_mean(offsets, 0.0)


def point_by_month(entry: dict[str, Any], month: str) -> dict[str, Any] | None:
    return next((point for point in entry.get("history", []) if point.get("month") == month), None)


def latest_history_window(entry: dict[str, Any], month: str, size: int = 12) -> list[dict[str, Any]]:
    rows = []
    for hist_month, value in history_mm(entry, seasonal=False):
        if hist_month < month and value is not None:
            rows.append({"month": hist_month, "nsa_mm": value})
    return rows[-size:]


def production_rows_by_code(forecast: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["itemCode"]: row for row in forecast.get("components", [])}


def challenger_component_rows_by_code(challenger: dict[str, Any], month: str) -> dict[str, dict[str, Any]]:
    current = challenger.get("currentForecast") or {}
    if current.get("forecastMonth") == month:
        return {row["series"]: row for row in current.get("componentRows", [])}
    out: dict[str, dict[str, Any]] = {}
    for code, rows in (challenger.get("componentSeries") or {}).items():
        row = next((item for item in rows if item.get("month") == month), None)
        if row:
            out[code] = row
    return out


def prediction_value(
    *,
    model: str,
    code: str,
    month: str,
    entry: dict[str, Any],
    production_by_code: dict[str, dict[str, Any]],
    challenger_by_code: dict[str, dict[str, Any]],
) -> dict[str, Any] | None:
    if model == "production":
        row = production_by_code.get(code)
        if row:
            nsa = row.get("forecast_nsa_mm")
            sa = row.get("forecast_sa_mm")
            interval = row.get("sigma")
            return {
                "nsa": nsa,
                "sa": sa,
                "tier": row.get("tier"),
                "fallback": row.get("driverSnapshot") or row.get("modelType") or "model",
                "p10": None if sa is None or not interval else float(sa) - 1.28155 * float(interval),
                "p50": sa,
                "p90": None if sa is None or not interval else float(sa) + 1.28155 * float(interval),
            }
        row = challenger_by_code.get(code)
        if row:
            nsa = row.get("productionNsaMm")
            sa = row.get("productionSaMm")
            if sa is None and nsa is not None:
                sa = float(nsa) + (seasonal_offset(entry, month) or 0.0)
            return {
                "nsa": nsa,
                "sa": sa,
                "tier": row.get("tier"),
                "fallback": "backtest_artifact",
                "p10": None,
                "p50": sa,
                "p90": None,
            }
    row = challenger_by_code.get(code)
    if not row:
        return None
    field = CHALLENGER_FIELD[model]
    if field in row and isinstance(row[field], dict):
        nsa = row[field].get("nsaMm")
        sa = row[field].get("saMm")
    else:
        nsa = row.get(f"{field}NsaMm")
        sa = row.get(f"{field}SaMm")
        if sa is None and nsa is not None:
            offset = seasonal_offset(entry, month) or 0.0
            sa = float(nsa) + offset
    return {
        "nsa": nsa,
        "sa": sa,
        "tier": row.get("tier"),
        "fallback": "challenger_window",
        "p10": None,
        "p50": sa,
        "p90": None,
    }


def build_prediction_rows(month: str, run_id: str, forecast: dict[str, Any], challenger: dict[str, Any]) -> list[dict[str, Any]]:
    production_by_code = production_rows_by_code(forecast)
    challenger_by_code = challenger_component_rows_by_code(challenger, month)
    rows: list[dict[str, Any]] = []
    missing: list[str] = []
    for entry in current_components():
        code = entry["itemCode"]
        weight = entry.get("currentRi")
        for model in MODELS:
            pred = prediction_value(
                model=model,
                code=code,
                month=month,
                entry=entry,
                production_by_code=production_by_code,
                challenger_by_code=challenger_by_code,
            )
            if not pred or pred.get("nsa") is None or pred.get("sa") is None:
                missing.append(f"{code} {entry['name']} / {model}")
                continue
            nsa = float(pred["nsa"])
            sa = float(pred["sa"])
            rows.append(
                {
                    "forecast_month": month,
                    "item_code": code,
                    "name": entry["name"],
                    "model": model,
                    "tier": pred.get("tier"),
                    "predicted_nsa_mm": nsa,
                    "predicted_sa_mm": sa,
                    "seasonal_factor_used": sa - nsa,
                    "weight_RI_used": weight,
                    "weight_vintage": forecast.get("dataThrough") or latest_month(),
                    "contribution_pp": None if weight is None else float(weight) * sa,
                    "fallback_level": pred.get("fallback"),
                    "interval_p10": pred.get("p10"),
                    "interval_p50": pred.get("p50"),
                    "interval_p90": pred.get("p90"),
                    "source_run_id": run_id,
                }
            )
    if missing:
        raise RuntimeError("Archive completeness check failed; missing predictions:\n" + "\n".join(missing[:200]))
    return rows


def formula_inputs(entry: dict[str, Any], month: str, model: str, run_id: str) -> list[dict[str, Any]]:
    values = latest_history_window(entry, month, 12)
    rows: list[dict[str, Any]] = []
    weights = {
        "production": [("last", 1, 0.55), ("trailing3", 3, 0.30), ("month_dummy", None, 0.15)],
        "seasonal_ar": [("month_dummy", None, 0.65), ("trailing6", 6, 0.35)],
        "hrnn": [("window", None, None), ("parent_prior", 1, None), ("checkpoint_id", None, None)],
        "i_gru": [("window", None, None), ("checkpoint_id", None, None)],
    }[model]
    for name, lag, weight in weights:
        if name == "window":
            value: Any = values
        elif name == "checkpoint_id":
            value = "challenger/hrnn/results.json"
        elif name == "parent_prior":
            value = entry.get("parent")
        elif name == "trailing3":
            value = [item["nsa_mm"] for item in values[-3:]]
        elif name == "trailing6":
            value = [item["nsa_mm"] for item in values[-6:]]
        elif name == "last":
            value = values[-1]["nsa_mm"] if values else None
        else:
            value = f"month_dummy_{month[-2:]}"
        rows.append(
            {
                "forecast_month": month,
                "item_code": entry["itemCode"],
                "model": model,
                "input_name": name if name != "month_dummy" else f"month_dummy_{month[-2:]}",
                "input_value": json.dumps(value, sort_keys=True, default=str),
                "input_publish_date": latest_month(),
                "lag_months": lag,
                "beta_or_weight_applied": weight,
                "checkpoint_id": "challenger/hrnn/results.json" if model in {"hrnn", "i_gru"} else None,
                "source_run_id": run_id,
            }
        )
    return rows


def production_driver_inputs(row: dict[str, Any], month: str, run_id: str) -> list[dict[str, Any]]:
    out = []
    if row.get("itemCode") == "SEHB":
        feed = row.get("feedStatus") or {}
        model = feed.get("lodgingModel") or {}
        adr_beta = model.get("adrBeta")
        for observation in feed.get("observationsUsed") or []:
            out.append(
                {
                    "forecast_month": month,
                    "item_code": "SEHB",
                    "model": "production",
                    "input_name": f"costar_str_weekly_adr_{observation.get('date')}",
                    "input_value": json.dumps(
                        {
                            "adr": observation.get("value"),
                            "occupancy": observation.get("occupancy"),
                            "source_url": observation.get("url"),
                        },
                        sort_keys=True,
                    ),
                    "input_publish_date": observation.get("publicationDate"),
                    "lag_months": 0,
                    "beta_or_weight_applied": adr_beta,
                    "checkpoint_id": None,
                    "source_run_id": run_id,
                }
            )
    for name in row.get("inputSeries") or []:
        out.append(
            {
                "forecast_month": month,
                "item_code": row["itemCode"],
                "model": "production",
                "input_name": str(name).replace(" ", "_").lower(),
                "input_value": json.dumps(row.get("driverSnapshot") or row.get("fallback_driver") or ""),
                "input_publish_date": latest_month(),
                "lag_months": None,
                "beta_or_weight_applied": None,
                "checkpoint_id": None,
                "source_run_id": run_id,
            }
        )
    return out


def build_input_rows_by_model(month: str, run_id: str, forecast: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    production_by_code = production_rows_by_code(forecast)
    out = {model: [] for model in MODELS}
    for entry in current_components():
        code = entry["itemCode"]
        for model in MODELS:
            out[model].extend(formula_inputs(entry, month, model, run_id))
        if code in production_by_code:
            out["production"].extend(production_driver_inputs(production_by_code[code], month, run_id))
    return out


def build_manifest(
    *,
    month: str,
    run_id: str,
    prediction_count: int,
    input_count_by_model: dict[str, int],
    forecast: dict[str, Any],
) -> dict[str, Any]:
    config_hashes = {
        "production": stable_hash(
            {
                "forecast_py": file_hash(MODEL_ROOT / "cpi_model" / "forecast.py"),
                "extended_registry": file_hash(MODEL_ROOT / "extended_registry.json"),
            }
        ),
        "hrnn": stable_hash({"run_py": file_hash(MODEL_ROOT / "challenger" / "hrnn" / "run.py"), "artifact": file_hash(challenger_path())}),
        "i_gru": stable_hash({"run_py": file_hash(MODEL_ROOT / "challenger" / "hrnn" / "run.py"), "artifact": file_hash(challenger_path())}),
        "seasonal_ar": stable_hash({"run_py": file_hash(MODEL_ROOT / "challenger" / "hrnn" / "run.py"), "artifact": file_hash(challenger_path())}),
    }
    snapshot = {
        "dashboard_cache": file_hash(DASHBOARD_ROOT / "src" / "data" / "dashboard-cache.json"),
        "forecast": stable_hash(forecast),
        "data_through": forecast.get("dataThrough") or latest_month(),
    }
    return {
        "run_id": run_id,
        "forecast_month": month,
        "exported_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "source_git_sha": source_git_sha(),
        "bls_reference_month": forecast.get("dataThrough") or latest_month(),
        "data_snapshot_id": stable_hash(snapshot),
        "model_config_hashes": config_hashes,
        "archive_schema_version": ARCHIVE_SCHEMA_VERSION,
        "component_count": len(current_components()),
        "prediction_count": prediction_count,
        "input_count_by_model": input_count_by_model,
        "notes": [
            "Archive stores the non-overlapping production forecast universe to avoid parent/child double-counting.",
            "Challenger rows are deterministic walk-forward artifacts from challenger/hrnn/results.json.",
        ],
    }


def assert_no_secrets(path: Path) -> None:
    offenders: list[str] = []
    for candidate in path.rglob("*"):
        if not candidate.is_file():
            continue
        if candidate.suffix.lower() in {".parquet", ".pyc"}:
            continue
        text = candidate.read_text(encoding="utf-8", errors="ignore")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                offenders.append(f"{candidate}: {pattern.pattern}")
                break
    if offenders:
        raise RuntimeError("Secret scan failed:\n" + "\n".join(offenders[:50]))


def write_parquet(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_parquet(path, index=False)


def git_commit(run_id: str, component_count: int) -> None:
    root = archive_root()
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    status = subprocess.run(["git", "status", "--porcelain"], cwd=root, check=True, capture_output=True, text=True)
    if not status.stdout.strip():
        return
    month = month_from_run_id(run_id)
    message = f"run {month}: 4 models, {component_count} components"
    if run_id != month:
        message = f"{message} ({run_id})"
    subprocess.run(["git", "commit", "-m", message], cwd=root, check=True)


def export_month(month: str, *, commit: bool = True, run_id: str | None = None) -> Path:
    ensure_archive_repo()
    forecast_path = dashboard_forecast_path()
    local_forecast = RUNS_DIR / month / "forecast.json"
    if local_forecast.exists():
        forecast = read_json(local_forecast)
    elif forecast_path.exists():
        forecast = read_json(forecast_path)
    else:
        raise FileNotFoundError(f"Missing forecast artifact: {forecast_path} or {local_forecast}")
    if forecast.get("forecastMonth") != month:
        raise RuntimeError(f"Latest forecast artifact is for {forecast.get('forecastMonth')}, not {month}. Run cpi_model.forecast first.")
    if not challenger_path().exists():
        raise FileNotFoundError(f"Missing challenger artifact: {challenger_path()}")
    challenger = read_json(challenger_path())
    run_id = run_id or choose_run_id(month)
    run_dir = archive_root() / "runs" / run_id
    if run_dir.exists():
        raise FileExistsError(f"Archive run already exists: {run_dir}")
    try:
        prediction_rows = build_prediction_rows(month, run_id, forecast, challenger)
        input_rows_by_model = build_input_rows_by_model(month, run_id, forecast)
        write_parquet(run_dir / "predictions.parquet", prediction_rows)
        for model, rows in input_rows_by_model.items():
            write_parquet(run_dir / "inputs" / f"{model}.parquet", rows)
        manifest = build_manifest(
            month=month,
            run_id=run_id,
            prediction_count=len(prediction_rows),
            input_count_by_model={model: len(rows) for model, rows in input_rows_by_model.items()},
            forecast=forecast,
        )
        write_json(run_dir / "manifest.json", manifest)
        assert_no_secrets(run_dir)
        if commit:
            git_commit(run_id, len(current_components()))
        return run_dir
    except Exception:
        if run_dir.exists() and not any(run_dir.glob("actuals.parquet")):
            import shutil

            shutil.rmtree(run_dir)
        raise


def actual_for(entry: dict[str, Any], month: str) -> tuple[float | None, float | None]:
    point = point_by_month(entry, month)
    if not point:
        return None, None
    nsa = dict(history_mm(entry, seasonal=False)).get(month)
    sa = point.get("saMm")
    return nsa, sa


def score_month(month: str, *, commit: bool = True) -> Path:
    ensure_archive_repo()
    runs_dir = archive_root() / "runs"
    candidates = sorted(path for path in runs_dir.glob(f"{month}*") if path.is_dir())
    if not candidates:
        raise FileNotFoundError(f"No archived run found for {month}")
    run_dir = candidates[-1]
    predictions = pd.read_parquet(run_dir / "predictions.parquet")
    by_code = entry_by_code()
    rows = []
    missing_actuals: list[str] = []
    for row in predictions.to_dict("records"):
        entry = by_code.get(row["item_code"])
        if not entry:
            missing_actuals.append(row["item_code"])
            continue
        actual_nsa, actual_sa = actual_for(entry, month)
        if actual_nsa is None and actual_sa is None:
            missing_actuals.append(row["item_code"])
            continue
        rows.append(
            {
                "forecast_month": month,
                "item_code": row["item_code"],
                "name": row["name"],
                "model": row["model"],
                "actual_nsa_mm": actual_nsa,
                "actual_sa_mm": actual_sa,
                "predicted_nsa_mm": row.get("predicted_nsa_mm"),
                "predicted_sa_mm": row.get("predicted_sa_mm"),
                "error_nsa_mm": None if actual_nsa is None else row.get("predicted_nsa_mm") - actual_nsa,
                "error_sa_mm": None if actual_sa is None else row.get("predicted_sa_mm") - actual_sa,
                "source_run_id": run_dir.name,
            }
        )
    if missing_actuals:
        raise RuntimeError(f"Actuals unavailable for {month}; missing {len(set(missing_actuals))} components.")
    write_parquet(run_dir / "actuals.parquet", rows)
    assert_no_secrets(run_dir)
    if commit:
        git_commit(run_dir.name, len(current_components()))
    return run_dir / "actuals.parquet"


def backfill_existing(*, commit: bool = True) -> list[Path]:
    """Replay existing local challenger months that can be represented honestly.

    Historical months use the challenger component-series artifact for all four
    displayed variants. Current production-only live feeds are not backfilled
    unless the artifact already contains the month/component prediction.
    """
    challenger = read_json(challenger_path())
    months = sorted({row["month"] for rows in (challenger.get("componentSeries") or {}).values() for row in rows})
    exported = []
    for month in months:
        if month >= latest_month():
            continue
        exported.append(export_backfill_month(month, challenger, commit=commit))
    return exported


def export_backfill_month(month: str, challenger: dict[str, Any], *, commit: bool = True) -> Path:
    ensure_archive_repo()
    run_id = choose_run_id(month)
    run_dir = archive_root() / "runs" / run_id
    fake_forecast = {"forecastMonth": month, "dataThrough": add_months(month, -1), "components": []}
    prediction_rows = build_prediction_rows(month, run_id, fake_forecast, challenger)
    input_rows_by_model = build_input_rows_by_model(month, run_id, fake_forecast)
    write_parquet(run_dir / "predictions.parquet", prediction_rows)
    for model, rows in input_rows_by_model.items():
        write_parquet(run_dir / "inputs" / f"{model}.parquet", rows)
    manifest = build_manifest(
        month=month,
        run_id=run_id,
        prediction_count=len(prediction_rows),
        input_count_by_model={model: len(rows) for model, rows in input_rows_by_model.items()},
        forecast=fake_forecast,
    )
    manifest["notes"].append("Backfill run from challenger componentSeries artifact; production is the archived tier/proxy series in that artifact.")
    write_json(run_dir / "manifest.json", manifest)
    assert_no_secrets(run_dir)
    if commit:
        git_commit(run_id, len(current_components()))
    return run_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Export CPI model runs to the local append-only archive.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--month", help="Forecast month YYYY-MM to export.")
    group.add_argument("--score", help="Forecast month YYYY-MM to score after BLS release.")
    group.add_argument("--backfill", action="store_true", help="Backfill existing local challenger/backtest months.")
    parser.add_argument("--no-commit", action="store_true", help="Write files without committing, for tests/debugging.")
    args = parser.parse_args()
    if args.month:
        run_dir = export_month(args.month, commit=not args.no_commit)
        print(f"Wrote archive run {run_dir}")
    elif args.score:
        actuals = score_month(args.score, commit=not args.no_commit)
        print(f"Wrote scored actuals {actuals}")
    else:
        runs = backfill_existing(commit=not args.no_commit)
        print(f"Backfilled {len(runs)} archive runs")


if __name__ == "__main__":
    main()
