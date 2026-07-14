from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cpi_model.data import entry_by_code, forecast_universe_codes

WORKSPACE = ROOT.parent
OUT_DIR = ROOT / "analysis" / "model_comparison"
DASHBOARD_OUT = WORKSPACE / "cpi-dashboard" / "src" / "data" / "challenger" / "model-comparison.json"
LABSTAT_PATH = WORKSPACE / "cpi-excel" / "data" / "raw" / "labstat" / "cu.data.0.Current"
CHALLENGER_PATH = ROOT / "challenger" / "hrnn" / "results.json"
CHALLENGER_DASHBOARD_PATH = WORKSPACE / "cpi-dashboard" / "src" / "data" / "challenger" / "results.json"
EIA_GASOLINE_PATH = ROOT / "data" / "feeds" / "eia" / "gasoline_regular.json"

MODELS = {
    "productionTier1": {"label": "Production Tier 1 fallback", "color": "#2563eb"},
    "productionTier3": {"label": "Production Tier 3 fallback", "color": "#dc2626"},
    "hrnn": {"label": "HRNN", "color": "#0f766e"},
    "iGru": {"label": "I-GRU", "color": "#7c3aed"},
    "seasonalAr": {"label": "Challenger Seasonal AR", "color": "#f59e0b"},
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, allow_nan=False), encoding="utf-8")


def month_from_labstat(year: str, period: str) -> str | None:
    if not period.startswith("M") or period == "M13":
        return None
    return f"{year}-{period[1:].zfill(2)}"


def load_actual() -> dict[str, dict[str, float | None]]:
    rows = []
    with LABSTAT_PATH.open(encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for raw in reader:
            raw = {str(key).strip(): value for key, value in raw.items()}
            series = raw["series_id"].strip()
            if series not in {"CUSR0000SA0", "CUUR0000SA0"}:
                continue
            month = month_from_labstat(raw["year"].strip(), raw["period"].strip())
            if not month:
                continue
            try:
                value = float(raw["value"])
            except ValueError:
                continue
            rows.append({"month": month, "series": series, "index": value})
    by_month: dict[str, dict[str, float | None]] = {}
    for row in sorted(rows, key=lambda item: item["month"]):
        slot = by_month.setdefault(row["month"], {"month": row["month"], "saIndex": None, "nsaIndex": None})
        if row["series"] == "CUSR0000SA0":
            slot["saIndex"] = row["index"]
        else:
            slot["nsaIndex"] = row["index"]
    months = sorted(by_month)
    for month in months:
        prev = by_month.get(add_months(month, -1), {})
        year_ago = by_month.get(add_months(month, -12), {})
        row = by_month[month]
        row["actualSaMm"] = pct_change(row.get("saIndex"), prev.get("saIndex"))
        row["actualNsaMm"] = pct_change(row.get("nsaIndex"), prev.get("nsaIndex"))
        row["actualSaYoy"] = pct_change(row.get("saIndex"), year_ago.get("saIndex"))
        row["actualNsaYoy"] = pct_change(row.get("nsaIndex"), year_ago.get("nsaIndex"))
    return by_month


def add_months(month: str, offset: int) -> str:
    year = int(month[:4])
    mon = int(month[5:])
    idx = year * 12 + mon - 1 + offset
    return f"{idx // 12:04d}-{idx % 12 + 1:02d}"


def pct_change(current: float | None, prior: float | None) -> float | None:
    if current is None or prior in {None, 0}:
        return None
    return float(current) / float(prior) - 1.0


def safe_mean(values: list[float | None], default: float = 0.0) -> float:
    clean = [float(value) for value in values if value is not None and math.isfinite(float(value))]
    return sum(clean) / len(clean) if clean else default


def monthly_average(points: list[dict[str, Any]], month: str) -> float | None:
    values = [float(point["value"]) for point in points if str(point.get("date", "")).startswith(month)]
    return sum(values) / len(values) if values else None


def load_eia_gasoline_points() -> list[dict[str, Any]]:
    if not EIA_GASOLINE_PATH.exists():
        return []
    return read_json(EIA_GASOLINE_PATH).get("points") or []


def eia_gasoline_forecast(month: str, points: list[dict[str, Any]]) -> float | None:
    current = monthly_average(points, month)
    prior = monthly_average(points, add_months(month, -1))
    if current is None or prior in {None, 0}:
        return None
    return current / prior - 1.0


def rate_from_challenger(value: float | None, *, nsa: bool) -> float | None:
    if value is None:
        return None
    # Challenger NSA rows are stored as log changes. SA rows are an approximate
    # rate after adding a seasonal offset, so keep those in rate space.
    return math.expm1(float(value)) if nsa else float(value)


def model_yoy(actual: dict[str, dict[str, float | None]], month: str, mm: float | None, *, seasonal: bool) -> float | None:
    if mm is None:
        return None
    prior = actual.get(add_months(month, -1), {})
    year_ago = actual.get(add_months(month, -12), {})
    key = "saIndex" if seasonal else "nsaIndex"
    prior_index = prior.get(key)
    base = year_ago.get(key)
    if prior_index is None or base in {None, 0}:
        return None
    return float(prior_index) * (1.0 + float(mm)) / float(base) - 1.0


def component_series(entry: dict[str, Any]) -> list[dict[str, Any]]:
    history = entry.get("history", [])
    rows: list[dict[str, Any]] = []
    for point in history:
        prior = next((item for item in history if item["month"] == add_months(point["month"], -1)), None)
        rows.append(
            {
                "month": point["month"],
                "actualNsaMm": pct_change(point.get("nsaIndex"), prior.get("nsaIndex") if prior else None),
                "ri": point.get("ri") if point.get("ri") is not None else entry.get("currentRi"),
            }
        )
    return rows


def values_before(rows: list[dict[str, Any]], month: str) -> list[float]:
    return [float(row["actualNsaMm"]) for row in rows if row["month"] < month and row.get("actualNsaMm") is not None]


def same_month_before(rows: list[dict[str, Any]], month: str) -> list[float]:
    suffix = month[-2:]
    return [
        float(row["actualNsaMm"])
        for row in rows
        if row["month"] < month and row["month"][-2:] == suffix and row.get("actualNsaMm") is not None
    ]


def production_tier_forecast(rows: list[dict[str, Any]], month: str, tier: int) -> float | None:
    values = values_before(rows, month)
    if not values:
        return None
    last = values[-1]
    trailing3 = safe_mean(values[-3:], last)
    trailing6 = safe_mean(values[-6:], trailing3)
    seasonal = safe_mean(same_month_before(rows, month), trailing6)
    if tier == 1:
        return 0.55 * last + 0.30 * trailing3 + 0.15 * seasonal
    return 0.45 * last + 0.25 * trailing3 + 0.20 * seasonal + 0.10 * trailing6


def headline_sa_offset(actual: dict[str, dict[str, float | None]], month: str) -> float:
    suffix = month[-2:]
    offsets = [
        float(row["actualSaMm"]) - float(row["actualNsaMm"])
        for row in actual.values()
        if row["month"] < month
        and row["month"][-2:] == suffix
        and row.get("actualSaMm") is not None
        and row.get("actualNsaMm") is not None
    ]
    return safe_mean(offsets, 0.0)


def aggregate_leaf_formula_predictions(actual: dict[str, dict[str, float | None]]) -> dict[str, dict[str, dict[str, float | None]]]:
    entries = entry_by_code()
    leaf_codes = forecast_universe_codes(list(entries.values()))
    series_by_code = {code: component_series(entries[code]) for code in leaf_codes if code in entries}
    eia_gasoline_points = load_eia_gasoline_points()
    out: dict[str, dict[str, dict[str, float | None]]] = {}
    for month in sorted(actual):
        month_slot = out.setdefault(month, {})
        weighted = {"productionTier1": 0.0, "productionTier3": 0.0}
        denom = {"productionTier1": 0.0, "productionTier3": 0.0}
        for code, rows in series_by_code.items():
            eligible = [row for row in rows if row["month"] <= month]
            if not eligible:
                continue
            weight = float(eligible[-1].get("ri") or 0.0)
            if weight <= 0:
                continue
            if code == "SETB01":
                gas = eia_gasoline_forecast(month, eia_gasoline_points)
                tier1 = gas if gas is not None else production_tier_forecast(rows, month, 1)
                tier3 = gas if gas is not None else production_tier_forecast(rows, month, 3)
            else:
                tier1 = production_tier_forecast(rows, month, 1)
                tier3 = production_tier_forecast(rows, month, 3)
            if tier1 is not None:
                weighted["productionTier1"] += weight * tier1
                denom["productionTier1"] += weight
            if tier3 is not None:
                weighted["productionTier3"] += weight * tier3
                denom["productionTier3"] += weight
        offset = headline_sa_offset(actual, month)
        for model in ["productionTier1", "productionTier3"]:
            nsa = weighted[model] / denom[model] if denom[model] > 0 else None
            sa = None if nsa is None else nsa + offset
            month_slot[model] = {
                "saMm": sa,
                "nsaMm": nsa,
                "saYoy": model_yoy(actual, month, sa, seasonal=True),
                "nsaYoy": model_yoy(actual, month, nsa, seasonal=False),
            }
    return out


def load_predictions(actual: dict[str, dict[str, float | None]]) -> tuple[dict[str, dict[str, dict[str, float | None]]], list[str]]:
    notes: list[str] = []
    predictions = aggregate_leaf_formula_predictions(actual)
    notes.append(
        "Production Tier 1 and Tier 3 fallback lines are walk-forward leaf-aggregated baselines. SETB01 gasoline uses the cached EIA weekly regular gasoline calendar-month pass-through when available; all other components use the stated CPI-history fallback formulas. "
        "They do not include other live-feed overrides such as Manheim used vehicles, jet fuel, shelter rent overlays, or food feed scaffolding."
    )
    if not CHALLENGER_PATH.exists():
        notes.append(f"Missing challenger artifact: {CHALLENGER_PATH}")
    else:
        challenger = read_json(CHALLENGER_PATH)
        for row in challenger.get("rows", []):
            month = row["month"]
            slot = predictions.setdefault(month, {})
            for model in ["hrnn", "iGru", "seasonalAr"]:
                nsa = rate_from_challenger(row.get(f"{model}HeadlineNsaMm"), nsa=True)
                sa = rate_from_challenger(row.get(f"{model}HeadlineSaMm"), nsa=False)
                slot[model] = {
                    "saMm": sa,
                    "nsaMm": nsa,
                    "saYoy": model_yoy(actual, month, sa, seasonal=True),
                    "nsaYoy": model_yoy(actual, month, nsa, seasonal=False),
                }
        first = next((row.get("month") for row in challenger.get("rows", []) if row.get("hrnnHeadlineNsaMm") is not None), None)
        if first and first > "2000-01":
            notes.append(
                f"Existing challenger/hrnn/results.json starts at {first}; no ~2000 challenger prediction rows are present. "
                "Regenerate challenger/hrnn/results.json from an artifact with earlier BLS history to extend the line."
            )

    # The current pre-release one-step-ahead challenger values live beside the
    # dashboard artifact rather than in the historical walk-forward rows.
    if CHALLENGER_DASHBOARD_PATH.exists():
        current = read_json(CHALLENGER_DASHBOARD_PATH).get("currentForecast") or {}
        month = current.get("forecastMonth")
        headline = next((row for row in current.get("rows", []) if row.get("series") == "headline"), None)
        if month and headline:
            slot = predictions.setdefault(month, {})
            for model in MODELS:
                values = headline.get(model) or {}
                sa = values.get("saMm")
                nsa = values.get("nsaMm")
                if sa is not None or nsa is not None:
                    slot[model] = {
                        "saMm": sa,
                        "nsaMm": nsa,
                        "saYoy": values.get("saYoy"),
                        "nsaYoy": values.get("nsaYoy"),
                    }

    notes.append(
        "The full production model is still omitted. The existing backtest/C/results.json series is a headline "
        "history scaffold, not a replay of the full production tier forecast with component live feeds. The only "
        "real production forecast artifact currently present is the current 2026-06 run, which is too short for "
        "a historical comparison. Build monthly forecast.py snapshots using only as-of data to add a true production line."
    )
    return predictions, notes


def build_rows(actual: dict[str, dict[str, float | None]], predictions: dict[str, dict[str, dict[str, float | None]]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for month in sorted(actual):
        actual_row = actual[month]
        row: dict[str, Any] = {
            "month": month,
            "actualSaMm": actual_row.get("actualSaMm"),
            "actualNsaMm": actual_row.get("actualNsaMm"),
            "actualSaYoy": actual_row.get("actualSaYoy"),
            "actualNsaYoy": actual_row.get("actualNsaYoy"),
        }
        for model in MODELS:
            pred = predictions.get(month, {}).get(model, {})
            for key in ["saMm", "nsaMm", "saYoy", "nsaYoy"]:
                row[f"{model}{key[0].upper()}{key[1:]}"] = pred.get(key)
            for key in ["SaYoy", "NsaYoy"]:
                actual_key = f"actual{key}"
                pred_key = f"{model}{key}"
                row[f"{model}{key}ErrorBp"] = None if row.get(pred_key) is None or row.get(actual_key) is None else (row[pred_key] - row[actual_key]) * 10000.0
        rows.append(row)
    return rows


def clean_pairs(rows: list[dict[str, Any]], model: str, pred_key: str, actual_key: str, *, start: str | None = None) -> list[tuple[float, float]]:
    out = []
    for row in rows:
        if start and row["month"] < start:
            continue
        pred = row.get(f"{model}{pred_key}")
        actual = row.get(actual_key)
        if pred is not None and actual is not None:
            out.append((float(pred), float(actual)))
    return out


def mae(values: list[tuple[float, float]]) -> float | None:
    return None if not values else sum(abs(a - b) for a, b in values) / len(values)


def rmse(values: list[tuple[float, float]]) -> float | None:
    return None if not values else math.sqrt(sum((a - b) ** 2 for a, b in values) / len(values))


def model_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    common_start = "2022-01"
    summary = []
    for model, spec in MODELS.items():
        months = [row["month"] for row in rows if row.get(f"{model}SaMm") is not None]
        if not months:
            summary.append({"model": model, "label": spec["label"], "start": None, "end": None, "months": 0})
            continue
        summary.append(
            {
                "model": model,
                "label": spec["label"],
                "start": months[0],
                "end": months[-1],
                "months": len(months),
                "fullSaMmMae": mae(clean_pairs(rows, model, "SaMm", "actualSaMm")),
                "fullSaMmRmse": rmse(clean_pairs(rows, model, "SaMm", "actualSaMm")),
                "fullNsaMmMae": mae(clean_pairs(rows, model, "NsaMm", "actualNsaMm")),
                "fullNsaMmRmse": rmse(clean_pairs(rows, model, "NsaMm", "actualNsaMm")),
                "fullSaYoyMae": mae(clean_pairs(rows, model, "SaYoy", "actualSaYoy")),
                "fullSaYoyRmse": rmse(clean_pairs(rows, model, "SaYoy", "actualSaYoy")),
                "fullNsaYoyMae": mae(clean_pairs(rows, model, "NsaYoy", "actualNsaYoy")),
                "fullNsaYoyRmse": rmse(clean_pairs(rows, model, "NsaYoy", "actualNsaYoy")),
                "commonSaMmMae": mae(clean_pairs(rows, model, "SaMm", "actualSaMm", start=common_start)),
                "commonSaMmRmse": rmse(clean_pairs(rows, model, "SaMm", "actualSaMm", start=common_start)),
                "commonNsaMmMae": mae(clean_pairs(rows, model, "NsaMm", "actualNsaMm", start=common_start)),
                "commonNsaMmRmse": rmse(clean_pairs(rows, model, "NsaMm", "actualNsaMm", start=common_start)),
                "commonSaYoyMae": mae(clean_pairs(rows, model, "SaYoy", "actualSaYoy", start=common_start)),
                "commonSaYoyRmse": rmse(clean_pairs(rows, model, "SaYoy", "actualSaYoy", start=common_start)),
                "commonNsaYoyMae": mae(clean_pairs(rows, model, "NsaYoy", "actualNsaYoy", start=common_start)),
                "commonNsaYoyRmse": rmse(clean_pairs(rows, model, "NsaYoy", "actualNsaYoy", start=common_start)),
            }
        )
    return summary


def to_dataframe(rows: list[dict[str, Any]]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["month"] + "-01")
    return df


def plot_mm(rows: list[dict[str, Any]], summary: list[dict[str, Any]]) -> None:
    df = to_dataframe(rows)
    fig, axes = plt.subplots(2, 1, figsize=(14, 9), sharey=False, constrained_layout=True)
    for ax, start, title in [
        (axes[0], None, "Headline CPI SA m/m: actual vs one-step-ahead predictions"),
        (axes[1], "2022-01", "Zoom: 2022-present"),
    ]:
        sub = df if start is None else df[df["month"] >= start]
        ax.plot(sub["date"], sub["actualSaMm"] * 100, color="#111827", linewidth=2.4, label="Actual SA m/m")
        for model, spec in MODELS.items():
            label = f"{spec['label']} ({next((item['start'] for item in summary if item['model'] == model), 'n/a')})"
            ax.plot(sub["date"], sub[f"{model}SaMm"] * 100, color=spec["color"], linewidth=1.2, label=label)
        ax.axvspan(pd.Timestamp("2022-01-01"), sub["date"].max(), color="#e0f2fe", alpha=0.18)
        ax.axhline(0, color="#94a3b8", linewidth=0.8)
        ax.set_title(title)
        ax.set_ylabel("percent m/m")
        ax.grid(True, axis="y", color="#e5e7eb")
        ax.legend(loc="upper left", ncols=2, fontsize=8)
    fig.savefig(OUT_DIR / "headline_mm_timeline.png", dpi=180)
    plt.close(fig)


def plot_yoy(rows: list[dict[str, Any]], summary: list[dict[str, Any]]) -> None:
    df = to_dataframe(rows)
    fig, axes = plt.subplots(3, 1, figsize=(14, 11), sharex=False, constrained_layout=True)
    panels = [
        (axes[0], None, "Headline CPI SA y/y: actual vs nowcast convention"),
        (axes[1], "2022-01", "Zoom: 2022-present"),
    ]
    for ax, start, title in panels:
        sub = df if start is None else df[df["month"] >= start]
        ax.plot(sub["date"], sub["actualSaYoy"] * 100, color="#111827", linewidth=2.4, label="Actual SA y/y")
        for model, spec in MODELS.items():
            label = f"{spec['label']} ({next((item['start'] for item in summary if item['model'] == model), 'n/a')})"
            ax.plot(sub["date"], sub[f"{model}SaYoy"] * 100, color=spec["color"], linewidth=1.2, label=label)
        ax.axvspan(pd.Timestamp("2022-01-01"), sub["date"].max(), color="#e0f2fe", alpha=0.18)
        ax.set_title(title + " - y/y = 11 actual months + 1 forecast month")
        ax.set_ylabel("percent y/y")
        ax.grid(True, axis="y", color="#e5e7eb")
        ax.legend(loc="upper left", ncols=2, fontsize=8)
    sub = df[df["month"] >= "2022-01"]
    for model, spec in MODELS.items():
        axes[2].plot(sub["date"], sub[f"{model}SaYoyErrorBp"], color=spec["color"], linewidth=1.1, label=spec["label"])
    axes[2].axhline(0, color="#94a3b8", linewidth=0.8)
    axes[2].set_title("SA y/y prediction error, predicted minus actual")
    axes[2].set_ylabel("basis points")
    axes[2].grid(True, axis="y", color="#e5e7eb")
    axes[2].legend(loc="upper left", ncols=4, fontsize=8)
    fig.savefig(OUT_DIR / "headline_yoy_timeline.png", dpi=180)
    plt.close(fig)


def write_markdown(payload: dict[str, Any]) -> None:
    lines = [
        "# Headline Model Timeline Comparison",
        "",
        "Every prediction is sourced from existing walk-forward artifacts; no models were retrained.",
        "",
        "Y/y = 11 actual months + 1 forecast month.",
        "",
        "## Model availability",
        "",
        "| Model | Start | End | Months | Full SA m/m MAE | Full SA m/m RMSE | Full SA y/y MAE | Full SA y/y RMSE | Common 2022+ SA m/m MAE | Common SA m/m RMSE | Common SA y/y MAE | Common SA y/y RMSE |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in payload["summary"]:
        fmt = lambda value: "n/a" if value is None else f"{value * 100:.3f}%"
        lines.append(
            f"| {row['label']} | {row.get('start') or 'n/a'} | {row.get('end') or 'n/a'} | {row.get('months', 0)} | "
            f"{fmt(row.get('fullSaMmMae'))} | {fmt(row.get('fullSaMmRmse'))} | {fmt(row.get('fullSaYoyMae'))} | {fmt(row.get('fullSaYoyRmse'))} | "
            f"{fmt(row.get('commonSaMmMae'))} | {fmt(row.get('commonSaMmRmse'))} | {fmt(row.get('commonSaYoyMae'))} | {fmt(row.get('commonSaYoyRmse'))} |"
        )
    lines.extend(["", "## Notes", ""])
    for note in payload["notes"]:
        lines.append(f"- {note}")
    (OUT_DIR / "timeline_comparison.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dashboard", action="store_true")
    args = parser.parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    actual = load_actual()
    predictions, notes = load_predictions(actual)
    rows = build_rows(actual, predictions)
    summary = model_summary(rows)
    payload = {
        "source": "Existing walk-forward challenger artifacts only; no retraining. Production scaffold is excluded.",
        "commonStart": "2022-01",
        "yoyConvention": "y/y = 11 actual months + 1 forecast month.",
        "models": MODELS,
        "summary": summary,
        "notes": notes,
        "rows": rows,
    }
    write_json(OUT_DIR / "model_comparison.json", payload)
    write_markdown(payload)
    pd.DataFrame(rows).to_csv(OUT_DIR / "model_comparison.csv", index=False)
    plot_mm(rows, summary)
    plot_yoy(rows, summary)
    if args.dashboard:
        write_json(DASHBOARD_OUT, payload)
    print(f"Wrote {OUT_DIR / 'model_comparison.json'}")
    print(f"Wrote {OUT_DIR / 'headline_mm_timeline.png'}")
    print(f"Wrote {OUT_DIR / 'headline_yoy_timeline.png'}")
    if args.dashboard:
        print(f"Wrote {DASHBOARD_OUT}")


if __name__ == "__main__":
    main()
