"""STEO-vs-BLS electricity analysis.

Parts:
  a) Levels & alignment: STEO nominal price m/m vs CPI electricity NSA m/m.
  b) Honest nowcast test: real-time STEO vintages vs production model, seasonal AR,
     Henry Hub distributed lag. Plus t+1..t+3 horizons.
  c) Combination: production + STEO term, walk-forward window C (2022-01+).

All m/m in percentage points. Baselines are strictly causal (expanding window,
data < target month only). STEO predictors come from the vintage issued in the
target month (ex-ante, released ~2nd week, ~4 weeks before the CPI print).
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
HH_PATH = HERE.parents[1] / "data" / "feeds" / "eia" / "henry_hub.json"

# ---------------------------------------------------------------- month helpers
def add_months(ym: str, n: int) -> str:
    y, m = int(ym[:4]), int(ym[5:7])
    idx = y * 12 + (m - 1) + n
    return f"{idx // 12:04d}-{idx % 12 + 1:02d}"

def mnum(ym: str) -> int:
    return int(ym[:4]) * 12 + int(ym[5:7]) - 1

def cal_month(ym: str) -> int:
    return int(ym[5:7])

# ---------------------------------------------------------------- load data
def load_json(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))

bls = load_json(RAW / "bls_sehf01.json")
cpi_nsa = {p["month"]: p["value"] for p in bls["CUUR0000SEHF01"]}   # index level
cpi_sa = {p["month"]: p["value"] for p in bls["CUSR0000SEHF01"]}
steo_cur = {p["date"]: p["value"] for p in load_json(RAW / "steo_current_ESRCUUS.json")["points"]}
vintages = load_json(RAW / "steo_vintages.json")["vintages"]
V = {v["issue_month"]: {p["date"]: p["value"] for p in v["path"]} for v in vintages}

# CPI m/m in percent (NSA)
def series_mm(levels: dict) -> dict:
    out = {}
    for m in sorted(levels):
        pm = add_months(m, -1)
        if pm in levels and levels[pm]:
            out[m] = 100.0 * (levels[m] / levels[pm] - 1.0)
    return out

cpi_mm = series_mm(cpi_nsa)          # actual target (NSA m/m, %)
cpi_sa_mm = series_mm(cpi_sa)

# Henry Hub daily -> calendar-month average -> log m/m (%)
hh_daily = load_json(HH_PATH)["points"]
hh_by_month: dict[str, list] = {}
for p in hh_daily:
    hh_by_month.setdefault(p["date"][:7], []).append(p["value"])
hh_month = {m: float(np.mean(v)) for m, v in hh_by_month.items() if v}
hh_mm = {}
for m in sorted(hh_month):
    pm = add_months(m, -1)
    if pm in hh_month and hh_month[pm] > 0:
        hh_mm[m] = 100.0 * np.log(hh_month[m] / hh_month[pm])

# STEO m/m from a given vintage issue, for target month t (both legs same vintage)
def steo_vintage_mm(issue: str, target: str):
    path = V.get(issue)
    if not path:
        return None
    pm = add_months(target, -1)
    if target in path and pm in path and path[pm]:
        return 100.0 * (path[target] / path[pm] - 1.0)
    return None

# ---------------------------------------------------------------- stats helpers
def mae(pairs):
    d = [abs(a - b) for a, b in pairs]
    return float(np.mean(d)) if d else float("nan")

def rmse(pairs):
    d = [(a - b) ** 2 for a, b in pairs]
    return float(np.sqrt(np.mean(d))) if d else float("nan")

def corr(pairs):
    if len(pairs) < 3:
        return float("nan")
    x = np.array([a for a, _ in pairs]); y = np.array([b for _, b in pairs])
    if x.std() == 0 or y.std() == 0:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])

def bias(pairs):  # mean(pred - actual)
    return float(np.mean([p - a for p, a in pairs])) if pairs else float("nan")

# ---------------------------------------------------------------- baselines (causal)
sorted_cpi_months = [m for m in sorted(cpi_mm)]

def hist_before(t):
    """List of (month, mm) with month < t, ascending."""
    return [(m, cpi_mm[m]) for m in sorted_cpi_months if mnum(m) < mnum(t)]

def production_pred(t):
    h = hist_before(t)
    if len(h) < 6:
        return None
    vals = [v for _, v in h]
    last = vals[-1]
    trailing3 = float(np.mean(vals[-3:]))
    same = [v for m, v in h if cal_month(m) == cal_month(t)]
    seasonal = float(np.mean(same)) if same else trailing3
    return 0.55 * last + 0.30 * trailing3 + 0.15 * seasonal

def seasonal_ar_pred(t):
    h = hist_before(t)
    if len(h) < 30:
        return None
    seas = {}
    for cm in range(1, 13):
        vv = [v for m, v in h if cal_month(m) == cm]
        seas[cm] = float(np.mean(vv)) if vv else 0.0
    # deseasonalized AR(1) fit (no intercept)
    des = [(m, v - seas[cal_month(m)]) for m, v in h]
    x, y = [], []
    for i in range(1, len(des)):
        x.append(des[i - 1][1]); y.append(des[i][1])
    x = np.array(x); y = np.array(y)
    phi = float(np.dot(x, y) / np.dot(x, x)) if np.dot(x, x) > 0 else 0.0
    pm = add_months(t, -1)
    if pm not in cpi_mm:
        return None
    des_prev = cpi_mm[pm] - seas[cal_month(pm)]
    return seas[cal_month(t)] + phi * des_prev

HH_LAGS = 6
def henryhub_pred(t):
    """OLS of CPI NSA m/m on HH log m/m, lags 0..HH_LAGS, expanding window."""
    h = hist_before(t)
    if len(h) < 36:
        return None
    rows_x, rows_y = [], []
    for m, y in h:
        feats = [hh_mm.get(add_months(m, -j)) for j in range(HH_LAGS + 1)]
        if any(f is None for f in feats):
            continue
        rows_x.append([1.0] + feats); rows_y.append(y)
    if len(rows_x) < 30:
        return None
    A = np.array(rows_x); b = np.array(rows_y)
    beta, *_ = np.linalg.lstsq(A, b, rcond=None)
    feats_t = [hh_mm.get(add_months(t, -j)) for j in range(HH_LAGS + 1)]
    if any(f is None for f in feats_t):
        return None
    return float(np.dot(beta, [1.0] + feats_t)), beta

def henryhub_value(t):
    r = henryhub_pred(t)
    return r[0] if isinstance(r, tuple) else r

# ---------------------------------------------------------------- PART B: nowcast
EVAL_START = "2015-01"
targets = [m for m in sorted_cpi_months if mnum(m) >= mnum(EVAL_START) and m in cpi_mm]

records = []
for t in targets:
    actual = cpi_mm.get(t)
    if actual is None:
        continue
    rec = {"month": t, "actual": actual}
    rec["steo_now"] = steo_vintage_mm(t, t)            # issue==t nowcast (headline)
    rec["steo_prev"] = steo_vintage_mm(add_months(t, -1), t)  # issue==t-1, 1mo-ahead
    rec["steo_next"] = steo_vintage_mm(add_months(t, 1), t)   # issue==t+1 sensitivity
    rec["prod"] = production_pred(t)
    rec["sar"] = seasonal_ar_pred(t)
    rec["hh"] = henryhub_value(t)
    records.append(rec)

def pairs_for(key, start=None):
    out = []
    for r in records:
        if start and mnum(r["month"]) < mnum(start):
            continue
        if r.get(key) is not None and r.get("actual") is not None:
            out.append((r[key], r["actual"]))
    return out

# Common sample: months where all headline predictors exist
def common_records(keys, start="2016-01"):
    return [r for r in records if mnum(r["month"]) >= mnum(start)
            and all(r.get(k) is not None for k in keys)]

METHODS = [("steo_now", "STEO nowcast (issue=t)"),
           ("prod", "Production model"),
           ("sar", "Seasonal AR(1)"),
           ("hh", "Henry Hub dist. lag")]
common = common_records([k for k, _ in METHODS])
common_months = [r["month"] for r in common]
tableB = []
for key, label in METHODS:
    prs = [(r[key], r["actual"]) for r in common]
    tableB.append((label, key, mae(prs), rmse(prs), corr(prs), bias(prs), len(prs)))

# STEO variants (own availability, honest span)
steo_variants = []
for key, label in [("steo_now", "STEO issue=t (nowcast, ~4wk lead)"),
                   ("steo_prev", "STEO issue=t-1 (1mo-ahead)"),
                   ("steo_next", "STEO issue=t+1 (fresher, ~days before print)")]:
    prs = pairs_for(key)
    steo_variants.append((label, key, mae(prs), rmse(prs), corr(prs), bias(prs), len(prs)))

# ---------------------------------------------------------------- PART B: horizons
# From vintage issued month M, forecast m/m for M+h vs actual CPI m/m at M+h.
# Compare STEO to a seasonal baseline (same-calendar-month mean known at M).
horizons = {}
for h in range(0, 4):
    steo_pairs, seas_pairs = [], []
    for v in vintages:
        M = v["issue_month"]
        t = add_months(M, h)
        if t not in cpi_mm:
            continue
        s = steo_vintage_mm(M, t)
        if s is None:
            continue
        # seasonal baseline computed from CPI history strictly before M (known at issue)
        hh_ = [(m, cpi_mm[m]) for m in sorted_cpi_months if mnum(m) < mnum(M)]
        same = [val for m, val in hh_ if cal_month(m) == cal_month(t)]
        if len(hh_) < 12 or not same:
            continue
        seas = float(np.mean(same))
        a = cpi_mm[t]
        steo_pairs.append((s, a)); seas_pairs.append((seas, a))
    horizons[h] = {
        "n": len(steo_pairs),
        "steo_mae": mae(steo_pairs), "steo_corr": corr(steo_pairs),
        "seas_mae": mae(seas_pairs), "seas_corr": corr(seas_pairs),
    }

# ---------------------------------------------------------------- innovation test
# Does STEO carry any signal BEYOND seasonality? Deseasonalize both sides with a
# causal (expanding) same-calendar-month mean and correlate the innovations.
def steo_now_history_before(t):
    """(month, steo_now_mm) for issue==month vintages with month < t."""
    out = []
    for m in sorted(cpi_mm):
        if mnum(m) >= mnum(t):
            continue
        s = steo_vintage_mm(m, m)
        if s is not None:
            out.append((m, s))
    return out

innov_pairs = []
for r in records:
    t = r["month"]
    if r.get("steo_now") is None or r.get("actual") is None:
        continue
    ch = hist_before(t)
    cpi_same = [v for m, v in ch if cal_month(m) == cal_month(t)]
    sh = steo_now_history_before(t)
    steo_same = [v for m, v in sh if cal_month(m) == cal_month(t)]
    if len(ch) < 24 or len(sh) < 24 or not cpi_same or not steo_same:
        continue
    cpi_innov = r["actual"] - float(np.mean(cpi_same))
    steo_innov = r["steo_now"] - float(np.mean(steo_same))
    innov_pairs.append((steo_innov, cpi_innov))
innov_corr = corr(innov_pairs)

# ---------------------------------------------------------------- PART C: combination (window C)
WIN_C = "2022-01"
def walk_forward_combo(feat_keys):
    """Expanding OLS: actual ~ 1 + feats, refit each month, predict (window C)."""
    rows = [r for r in records if all(r.get(k) is not None for k in feat_keys)
            and r.get("actual") is not None]
    rows.sort(key=lambda r: r["month"])
    out = []
    for r in rows:
        if mnum(r["month"]) < mnum(WIN_C):
            continue
        train = [x for x in rows if mnum(x["month"]) < mnum(r["month"])]
        if len(train) < 24:
            continue
        A = np.array([[1.0] + [x[k] for k in feat_keys] for x in train])
        b = np.array([x["actual"] for x in train])
        beta, *_ = np.linalg.lstsq(A, b, rcond=None)
        pred = float(np.dot(beta, [1.0] + [r[k] for k in feat_keys]))
        out.append({"month": r["month"], "actual": r["actual"], "pred": pred,
                    "beta": beta.tolist()})
    return out

# Production + STEO walk-forward combo; attach component values for plotting.
comboC = walk_forward_combo(["prod", "steo_now"])
rec_by_month = {r["month"]: r for r in records}
for r in comboC:
    src = rec_by_month[r["month"]]
    r["combo"] = r["pred"]
    r["prod"] = src["prod"]
    r["steo"] = src["steo_now"]
    r["sar"] = src.get("sar")

tableC = []
tableC.append(("Production + STEO (walk-fwd combo)", mae([(r["combo"], r["actual"]) for r in comboC]),
               rmse([(r["combo"], r["actual"]) for r in comboC]),
               corr([(r["combo"], r["actual"]) for r in comboC]), len(comboC)))
for key, label in [("prod", "Production alone"), ("steo", "STEO nowcast alone"), ("sar", "Seasonal AR alone")]:
    prs = [(r[key], r["actual"]) for r in comboC if r.get(key) is not None]
    tableC.append((label, mae(prs), rmse(prs), corr(prs), len(prs)))

# Decisive combos: does STEO improve on each base model? Compare a two-feature
# combo (base + STEO) against a RECALIBRATED single-feature control (base only,
# same expanding-OLS intercept+slope). The MAE delta between them is STEO's true
# marginal value; comparing to the raw base would credit STEO with recalibration.
def combo_mae(feat_keys):
    rows = walk_forward_combo(feat_keys)
    return mae([(r["pred"], r["actual"]) for r in rows]), rows

prod_recal_mae, _ = combo_mae(["prod"])          # actual ~ 1 + prod
sar_recal_mae, _ = combo_mae(["sar"])            # actual ~ 1 + sar
prod_steo_mae, comboC = combo_mae(["prod", "steo_now"])
sar_steo_mae, comboSAR = combo_mae(["sar", "steo_now"])
# re-attach plot fields to the (rebuilt) comboC
for r in comboC:
    src = rec_by_month[r["month"]]
    r["combo"] = r["pred"]; r["prod"] = src["prod"]; r["steo"] = src["steo_now"]; r["sar"] = src.get("sar")
sar_only_mae = sar_recal_mae
avg_beta = np.mean([r["beta"] for r in comboC], axis=0) if comboC else [float("nan")] * 3
last_beta = comboC[-1]["beta"] if comboC else [float("nan")] * 3
avg_beta_sar = np.mean([r["beta"] for r in comboSAR], axis=0) if comboSAR else [float("nan")] * 3

# ---------------------------------------------------------------- PART A: levels & alignment
a_start = "2015-01"
a_months = [m for m in sorted(cpi_nsa) if mnum(m) >= mnum(a_start) and m in steo_cur and m in cpi_mm]
steo_cur_mm = series_mm(steo_cur)
a_pairs = [(steo_cur_mm[m], cpi_mm[m]) for m in a_months if m in steo_cur_mm]
# level indices normalized to 100 at a_start
def norm_index(levels, months, base):
    b = levels[base]
    return [100.0 * levels[m] / b for m in months]
lvl_months = [m for m in a_months if m in steo_cur and m in cpi_nsa]
base = lvl_months[0]
steo_idx = norm_index(steo_cur, lvl_months, base)
cpi_idx = norm_index(cpi_nsa, lvl_months, base)
a_slope, a_int = np.polyfit([p for p, _ in a_pairs], [q for _, q in a_pairs], 1)

# ================================================================ PLOTS
xs = lambda ms: [mnum(m) for m in ms]
def year_ticks(ax, months):
    ticks = [mnum(m) for m in months if m.endswith("-01")]
    labs = [m[:4] for m in months if m.endswith("-01")]
    ax.set_xticks(ticks); ax.set_xticklabels(labs, rotation=0)

# A1 levels overlay
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(xs(lvl_months), steo_idx, label="STEO nominal price (avg revenue/kWh)", color="#c0392b")
ax.plot(xs(lvl_months), cpi_idx, label="CPI electricity NSA (fixed-quantity index)", color="#2c3e50")
ax.set_title("Electricity price levels, indexed to 100 at 2015-01"); ax.set_ylabel("index (2015-01=100)")
year_ticks(ax, lvl_months); ax.legend(); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig(HERE / "fig_a1_levels_overlay.png", dpi=130); plt.close(fig)

# A2 m/m overlay
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(xs(a_months), [steo_cur_mm[m] for m in a_months], label="STEO price m/m", color="#c0392b", alpha=.8)
ax.plot(xs(a_months), [cpi_mm[m] for m in a_months], label="CPI electricity NSA m/m", color="#2c3e50", alpha=.8)
ax.axhline(0, color="k", lw=.5); ax.set_title("Month-over-month: STEO price vs CPI electricity (NSA), current vintage / in-sample")
ax.set_ylabel("% m/m"); year_ticks(ax, a_months); ax.legend(); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig(HERE / "fig_a2_mm_overlay.png", dpi=130); plt.close(fig)

# A3 scatter
fig, ax = plt.subplots(figsize=(6, 6))
px = [p for p, _ in a_pairs]; py = [q for _, q in a_pairs]
ax.scatter(px, py, s=14, alpha=.6, color="#2980b9")
lo, hi = min(px + py), max(px + py)
ax.plot([lo, hi], [lo, hi], "k--", lw=.8, label="45°")
xxx = np.linspace(lo, hi, 50); ax.plot(xxx, a_slope * xxx + a_int, color="#c0392b", label=f"fit slope={a_slope:.2f}")
ax.set_xlabel("STEO price m/m (%)"); ax.set_ylabel("CPI electricity NSA m/m (%)")
ax.set_title(f"Alignment 2015-present  r={corr(a_pairs):.2f}"); ax.legend(); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig(HERE / "fig_a3_scatter.png", dpi=130); plt.close(fig)

# B1 MAE bars
fig, ax = plt.subplots(figsize=(8, 5))
labels = [t[0] for t in tableB]; maes = [t[2] for t in tableB]
colors = ["#c0392b", "#7f8c8d", "#95a5a6", "#95a5a6"]
ax.bar(range(len(labels)), maes, color=colors)
for i, m in enumerate(maes):
    ax.text(i, m + .002, f"{m:.3f}", ha="center", fontsize=9)
ax.set_xticks(range(len(labels))); ax.set_xticklabels(labels, rotation=20, ha="right")
ax.set_ylabel("MAE (pp of m/m)"); ax.set_title(f"Honest nowcast MAE vs CPI electricity NSA m/m\ncommon sample {common_months[0]}..{common_months[-1]} (n={len(common)})")
ax.grid(axis="y", alpha=.3); fig.tight_layout(); fig.savefig(HERE / "fig_b1_nowcast_mae.png", dpi=130); plt.close(fig)

# B2 STEO nowcast scatter
fig, ax = plt.subplots(figsize=(6, 6))
prs = pairs_for("steo_now")
px = [p for p, _ in prs]; py = [q for _, q in prs]
ax.scatter(px, py, s=14, alpha=.6, color="#c0392b")
lo, hi = min(px + py), max(px + py); ax.plot([lo, hi], [lo, hi], "k--", lw=.8, label="45°")
ax.set_xlabel("STEO nowcast m/m (%)"); ax.set_ylabel("CPI electricity NSA m/m (%)")
ax.set_title(f"STEO real-time nowcast vs CPI  r={corr(prs):.2f}  n={len(prs)}"); ax.legend(); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig(HERE / "fig_b2_steo_scatter.png", dpi=130); plt.close(fig)

# B3 horizon MAE
fig, ax = plt.subplots(figsize=(8, 5))
hs = sorted(horizons)
ax.plot(hs, [horizons[h]["steo_mae"] for h in hs], "o-", color="#c0392b", label="STEO forecast")
ax.plot(hs, [horizons[h]["seas_mae"] for h in hs], "s--", color="#7f8c8d", label="Seasonal baseline")
ax.set_xlabel("horizon h (months ahead of issue)"); ax.set_ylabel("MAE (pp)")
ax.set_xticks(hs); ax.set_title("STEO forecast skill by horizon vs seasonal baseline")
ax.legend(); ax.grid(alpha=.3); fig.tight_layout(); fig.savefig(HERE / "fig_b3_horizon_mae.png", dpi=130); plt.close(fig)

# C1 combo series (window C)
if comboC:
    cm = [r["month"] for r in comboC]
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(xs(cm), [r["actual"] for r in comboC], "k-", lw=1.6, label="CPI actual")
    ax.plot(xs(cm), [r["prod"] for r in comboC], color="#7f8c8d", alpha=.8, label="Production")
    ax.plot(xs(cm), [r["steo"] for r in comboC], color="#c0392b", alpha=.8, label="STEO nowcast")
    ax.plot(xs(cm), [r["combo"] for r in comboC], color="#27ae60", lw=1.4, label="Combo (walk-fwd OLS)")
    ax.axhline(0, color="k", lw=.4); year_ticks(ax, cm)
    ax.set_ylabel("% m/m"); ax.set_title("Window C (2022-01+): CPI electricity NSA m/m — actual vs models")
    ax.legend(ncol=2); ax.grid(alpha=.3); fig.tight_layout(); fig.savefig(HERE / "fig_c1_combo_series.png", dpi=130); plt.close(fig)

# ================================================================ dump results json
def fmt_table(rows, cols):
    return {"columns": cols, "rows": rows}

results = {
    "spans": {
        "cpi_actual": [sorted_cpi_months[0], sorted_cpi_months[-1]],
        "steo_vintages": [vintages[0]["issue_month"], vintages[-1]["issue_month"]],
        "n_vintages": len(vintages),
        "nowcast_common_sample": [common_months[0], common_months[-1], len(common)],
    },
    "partA": {
        "n": len(a_pairs), "corr": corr(a_pairs), "fit_slope": float(a_slope), "fit_intercept": float(a_int),
        "mae_between_mm": mae(a_pairs), "mean_steo_mm": float(np.mean([p for p, _ in a_pairs])),
        "mean_cpi_mm": float(np.mean([q for _, q in a_pairs])),
        "steo_cum_growth_pct": float(steo_idx[-1] - 100), "cpi_cum_growth_pct": float(cpi_idx[-1] - 100),
        "level_span": [lvl_months[0], lvl_months[-1]],
    },
    "partB_methods": [dict(label=l, key=k, mae=ma, rmse=rm, corr=c, bias=bi, n=n) for (l, k, ma, rm, c, bi, n) in tableB],
    "partB_steo_variants": [dict(label=l, key=k, mae=ma, rmse=rm, corr=c, bias=bi, n=n) for (l, k, ma, rm, c, bi, n) in steo_variants],
    "partB_horizons": horizons,
    "partB_innovation": {
        "n": len(innov_pairs), "corr": innov_corr,
        "note": "Corr of STEO deseasonalized innovation vs CPI deseasonalized innovation (causal same-month means).",
    },
    "partC": {
        "window": "C (2022-01+)", "n": len(comboC),
        "table": [dict(label=l, mae=ma, rmse=rm, corr=c, n=n) for (l, ma, rm, c, n) in tableC],
        "prod_steo_avg_beta": [float(x) for x in avg_beta],
        "prod_steo_last_beta": [float(x) for x in last_beta],
        "prod_steo_beta_names": ["intercept", "production", "steo_nowcast"],
        "marginal_value_test": {
            "prod_recal_mae": prod_recal_mae, "prod_plus_steo_mae": prod_steo_mae,
            "prod_steo_marginal_delta": prod_recal_mae - prod_steo_mae,
            "sar_recal_mae": sar_recal_mae, "sar_plus_steo_mae": sar_steo_mae,
            "sar_steo_marginal_delta": sar_recal_mae - sar_steo_mae,
            "sar_steo_avg_beta": [float(x) for x in avg_beta_sar],
            "sar_steo_beta_names": ["intercept", "seasonal_ar", "steo_nowcast"],
            "note": "Delta = MAE(recalibrated base only) - MAE(base+STEO). Positive => STEO adds value beyond recalibration.",
        },
    },
    "henryhub_lags": HH_LAGS,
}
(HERE / "results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
print("Analysis complete.")
print(json.dumps(results, indent=2))
