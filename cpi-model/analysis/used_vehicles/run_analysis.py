"""Manheim (wholesale) -> BLS CPI used-cars (retail) pass-through analysis.

Walk-forward mindset throughout: cross-correlation by era, a distributed-lag
pass-through kernel (with an asymmetric up/down test), a retail-wholesale
level-gap / mean-reversion study, and a leakage-aware walk-forward nowcast.

Everything is computed from the two real series pulled by uv_data.py.  All
numbers written into report.md are produced here (never hand-typed), and the
fitted kernel is emitted to lag_weights.json.

Run:  python run_analysis.py
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller

import uv_data

HERE = Path(__file__).resolve().parent
MERGED_CSV = HERE / "usedcar_manheim.csv"

MAX_LAG = 4              # distributed-lag Manheim lags 0..4
XC_MAX = 6              # cross-correlation leads 0..6
WINDOW_C_START = "2022-01"   # backtest window C (see cpi_model/backtest.py)
NOWCAST_START = "2019-01"
CURRENT_KERNEL_LAGS = [1, 2]  # triage.py SETA02 pass_through_lags today

MANHEIM_MOM = "manheim_mom"
CPI_MOM = "cpi_sa_mom"

plt.rcParams.update({"font.size": 11, "axes.grid": True, "grid.alpha": 0.3, "figure.dpi": 130})
C_WHOLE = "#1f77b4"   # Manheim / wholesale
C_RETAIL = "#d62728"  # CPI / retail
C_ACC = "#2ca02c"


# --------------------------------------------------------------------------- #
# Data
# --------------------------------------------------------------------------- #
def load() -> tuple[pd.DataFrame, dict]:
    frame, meta = uv_data.build_merged(cache=True)
    frame["date"] = pd.to_datetime(frame["date"])
    frame = frame.sort_values("date").reset_index(drop=True)
    return frame, meta


def overlap(frame: pd.DataFrame) -> pd.DataFrame:
    """Months where both SA levels exist, indexed by date."""
    d = frame.dropna(subset=["manheim_sa", "cpi_used_sa"]).copy()
    d = d.set_index("date")
    return d


# --------------------------------------------------------------------------- #
# (a) rebased levels + m/m overlays
# --------------------------------------------------------------------------- #
def rebase(series: pd.Series, anchor: pd.Timestamp) -> pd.Series:
    base = series.loc[series.index <= anchor].dropna()
    if base.empty:
        base_val = series.dropna().iloc[0]
    else:
        base_val = base.iloc[-1]
    return series / base_val * 100.0


def fig_levels(df: pd.DataFrame, anchor: pd.Timestamp) -> Path:
    man = rebase(df["manheim_sa"], anchor)
    cpi = rebase(df["cpi_used_sa"], anchor)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for ax, lo, title in (
        (axes[0], df.index.min(), "Full sample"),
        (axes[1], pd.Timestamp("2019-01-01"), "2019 - present"),
    ):
        m = df.index >= lo
        ax.plot(df.index[m], man[m], color=C_WHOLE, lw=2, label="Manheim UVVI (wholesale, SA)")
        ax.plot(df.index[m], cpi[m], color=C_RETAIL, lw=2, label="CPI used cars & trucks (retail, SA)")
        ax.set_title(title)
        ax.set_ylabel(f"Index (rebased 100 = {anchor:%b %Y})")
        ax.legend(fontsize=9, loc="upper left")
    fig.suptitle("Wholesale vs retail used-vehicle price levels (rebased)", fontsize=13)
    fig.tight_layout()
    p = HERE / "fig1_levels_rebased.png"
    fig.savefig(p)
    plt.close(fig)
    return p


def fig_mom(df: pd.DataFrame) -> Path:
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=False)
    for ax, lo, title in (
        (axes[0], df.index.min(), "Full sample"),
        (axes[1], pd.Timestamp("2019-01-01"), "2019 - present"),
    ):
        m = df.index >= lo
        ax.plot(df.index[m], df[MANHEIM_MOM][m], color=C_WHOLE, lw=1.6, label="Manheim m/m %")
        ax.plot(df.index[m], df[CPI_MOM][m], color=C_RETAIL, lw=1.8, label="CPI used m/m %")
        ax.axhline(0, color="gray", lw=0.8)
        ax.set_title(title)
        ax.set_ylabel("m/m %")
        ax.legend(fontsize=9, loc="upper left")
    fig.suptitle("Month-over-month % change: Manheim (wholesale) vs CPI used (retail)", fontsize=13)
    fig.tight_layout()
    p = HERE / "fig2_mom_overlay.png"
    fig.savefig(p)
    plt.close(fig)
    return p


# --------------------------------------------------------------------------- #
# (b) cross-correlation by era (Manheim leads CPI by k months)
# --------------------------------------------------------------------------- #
ERAS = {
    "pre-2020": (None, "2019-12"),
    "COVID 2020-2022": ("2020-01", "2022-12"),
    "post-2022": ("2023-01", None),
}


def xcorr_by_era(df: pd.DataFrame) -> dict:
    out: dict[str, dict] = {}
    cpi = df[CPI_MOM]
    man = df[MANHEIM_MOM]
    for era, (lo, hi) in ERAS.items():
        mask = pd.Series(True, index=df.index)
        if lo:
            mask &= df.index >= pd.Timestamp(lo + "-01")
        if hi:
            mask &= df.index <= pd.Timestamp(hi + "-01")
        corrs = {}
        for k in range(XC_MAX + 1):
            pair = pd.concat([cpi[mask], man.shift(k)[mask]], axis=1).dropna()
            corrs[k] = float(pair.iloc[:, 0].corr(pair.iloc[:, 1])) if len(pair) > 8 else np.nan
        valid = {k: v for k, v in corrs.items() if not np.isnan(v)}
        peak = max(valid, key=valid.get) if valid else None
        out[era] = {
            "n": int(mask.sum()),
            "corr_by_lag": corrs,
            "peak_lag": peak,
            "peak_corr": corrs.get(peak) if peak is not None else None,
        }
    # full sample too
    corrs = {}
    for k in range(XC_MAX + 1):
        pair = pd.concat([cpi, man.shift(k)], axis=1).dropna()
        corrs[k] = float(pair.iloc[:, 0].corr(pair.iloc[:, 1]))
    peak = max(corrs, key=corrs.get)
    out["full"] = {"n": int(cpi.notna().sum()), "corr_by_lag": corrs, "peak_lag": peak, "peak_corr": corrs[peak]}
    return out


def fig_xcorr(xc: dict) -> Path:
    fig, ax = plt.subplots(figsize=(9.5, 5.4))
    colors = {"pre-2020": "#1f77b4", "COVID 2020-2022": "#d62728", "post-2022": "#2ca02c", "full": "black"}
    for era, res in xc.items():
        ks = list(res["corr_by_lag"])
        vs = [res["corr_by_lag"][k] for k in ks]
        lw = 2.6 if era == "full" else 1.9
        ls = "--" if era == "full" else "-"
        ax.plot(ks, vs, marker="o", color=colors[era], lw=lw, ls=ls, label=f"{era} (n={res['n']})")
        if res["peak_lag"] is not None:
            ax.scatter([res["peak_lag"]], [res["peak_corr"]], color=colors[era], s=70, zorder=5, edgecolor="white")
    ax.axvspan(1, 2, color="gray", alpha=0.12, label="expected 1-2m band")
    ax.set_xlabel("Lag k (months Manheim leads CPI)")
    ax.set_ylabel("corr( CPI used m/m , Manheim m/m shifted +k )")
    ax.set_title("Cross-correlation of wholesale vs retail m/m by era")
    ax.legend(fontsize=9)
    fig.tight_layout()
    p = HERE / "fig3_xcorr_by_era.png"
    fig.savefig(p)
    plt.close(fig)
    return p


# --------------------------------------------------------------------------- #
# (c) distributed-lag pass-through kernel + asymmetry
# --------------------------------------------------------------------------- #
def build_lag_matrix(df: pd.DataFrame, max_lag: int = MAX_LAG) -> pd.DataFrame:
    d = pd.DataFrame(index=df.index)
    d["y"] = df[CPI_MOM]
    d["y_lag1"] = df[CPI_MOM].shift(1)          # persistence term
    for k in range(max_lag + 1):
        d[f"m{k}"] = df[MANHEIM_MOM].shift(k)
    return d


def dl_regression(df: pd.DataFrame) -> dict:
    d = build_lag_matrix(df).dropna()
    xcols = [f"m{k}" for k in range(MAX_LAG + 1)] + ["y_lag1"]
    X = sm.add_constant(d[xcols])
    res = sm.OLS(d["y"], X).fit(cov_type="HAC", cov_kwds={"maxlags": XC_MAX})
    betas = {f"m{k}": float(res.params[f"m{k}"]) for k in range(MAX_LAG + 1)}
    se = {f"m{k}": float(res.bse[f"m{k}"]) for k in range(MAX_LAG + 1)}
    rho = float(res.params["y_lag1"])
    cum = float(sum(betas.values()))
    long_run = cum / (1 - rho) if abs(1 - rho) > 1e-6 else np.nan
    return {
        "n": int(res.nobs),
        "sample": [d.index.min().strftime("%Y-%m"), d.index.max().strftime("%Y-%m")],
        "intercept": float(res.params["const"]),
        "betas": betas,
        "betas_se": se,
        "persistence_rho": rho,
        "persistence_se": float(res.bse["y_lag1"]),
        "cumulative_passthrough": cum,      # sum of Manheim betas (impact + direct lags)
        "long_run_multiplier": float(long_run),  # cum / (1-rho): total incl. CPI persistence
        "r2": float(res.rsquared),
        "r2_adj": float(res.rsquared_adj),
    }


def dl_asymmetry(df: pd.DataFrame) -> dict:
    d = pd.DataFrame(index=df.index)
    d["y"] = df[CPI_MOM]
    d["y_lag1"] = df[CPI_MOM].shift(1)
    up = df[MANHEIM_MOM].clip(lower=0)
    dn = df[MANHEIM_MOM].clip(upper=0)
    for k in range(MAX_LAG + 1):
        d[f"up{k}"] = up.shift(k)
        d[f"dn{k}"] = dn.shift(k)
    d = d.dropna()
    xcols = [f"up{k}" for k in range(MAX_LAG + 1)] + [f"dn{k}" for k in range(MAX_LAG + 1)] + ["y_lag1"]
    X = sm.add_constant(d[xcols])
    res = sm.OLS(d["y"], X).fit(cov_type="HAC", cov_kwds={"maxlags": XC_MAX})
    cum_up = float(sum(res.params[f"up{k}"] for k in range(MAX_LAG + 1)))
    cum_dn = float(sum(res.params[f"dn{k}"] for k in range(MAX_LAG + 1)))
    # Wald test: equal cumulative up vs down pass-through
    r = np.zeros(len(X.columns))
    cols = list(X.columns)
    for k in range(MAX_LAG + 1):
        r[cols.index(f"up{k}")] = 1.0
        r[cols.index(f"dn{k}")] = -1.0
    wald = res.f_test(r.reshape(1, -1))
    return {
        "cum_passthrough_up": cum_up,
        "cum_passthrough_down": cum_dn,
        "up_betas": {f"up{k}": float(res.params[f"up{k}"]) for k in range(MAX_LAG + 1)},
        "down_betas": {f"dn{k}": float(res.params[f"dn{k}"]) for k in range(MAX_LAG + 1)},
        "wald_equal_pvalue": float(np.ravel(wald.pvalue)[0]),
        "r2": float(res.rsquared),
    }


def fig_kernel(dl: dict) -> Path:
    ks = list(range(MAX_LAG + 1))
    betas = [dl["betas"][f"m{k}"] for k in ks]
    ses = [dl["betas_se"][f"m{k}"] for k in ks]
    fig, ax = plt.subplots(figsize=(8.5, 5))
    ax.bar(ks, betas, yerr=[1.96 * s for s in ses], color=C_WHOLE, alpha=0.85, capsize=4,
           label="Manheim lag beta (+/-95% HAC)")
    ax.axhline(0, color="gray", lw=0.8)
    cum = np.cumsum(betas)
    ax.plot(ks, cum, color=C_RETAIL, marker="o", lw=2, label="cumulative pass-through")
    for k, c in zip(ks, cum):
        ax.annotate(f"{c:.2f}", (k, c), textcoords="offset points", xytext=(0, 8), color=C_RETAIL, fontsize=9)
    ax.set_xlabel("Manheim lag k (months)")
    ax.set_ylabel("beta on CPI used m/m")
    ax.set_title(f"Fitted pass-through kernel (persistence rho={dl['persistence_rho']:.2f}, "
                 f"cum={dl['cumulative_passthrough']:.2f}, R2={dl['r2']:.2f})")
    ax.set_xticks(ks)
    ax.legend(fontsize=9)
    fig.tight_layout()
    p = HERE / "fig4_lag_kernel.png"
    fig.savefig(p)
    plt.close(fig)
    return p


# --------------------------------------------------------------------------- #
# (d) level-gap / mean-reversion
# --------------------------------------------------------------------------- #
def level_gap(df: pd.DataFrame, anchor: pd.Timestamp) -> dict:
    man = rebase(df["manheim_sa"], anchor)
    cpi = rebase(df["cpi_used_sa"], anchor)
    gap = (cpi - man).dropna()          # retail minus wholesale, rebased index pts
    gap.name = "gap"
    mean = float(gap.mean())
    dev = gap - mean
    # mean reversion: d(gap)= a + lam*(gap[-1]-mean); lam<0 => reverting
    dd = pd.DataFrame({"dgap": gap.diff(), "dev_lag": dev.shift(1)}).dropna()
    X = sm.add_constant(dd["dev_lag"])
    mr = sm.OLS(dd["dgap"], X).fit(cov_type="HAC", cov_kwds={"maxlags": XC_MAX})
    lam = float(mr.params["dev_lag"])
    half_life = float(-np.log(2) / np.log(1 + lam)) if -2 < lam < 0 else np.nan
    adf = adfuller(gap.values, autolag="AIC")
    # spread as predictor: next-3-month cumulative CPI m/m on current gap deviation
    fwd3 = df[CPI_MOM].shift(-1) + df[CPI_MOM].shift(-2) + df[CPI_MOM].shift(-3)
    pr = pd.DataFrame({"fwd3": fwd3.reindex(gap.index), "dev": dev}).dropna()
    Xp = sm.add_constant(pr["dev"])
    pred = sm.OLS(pr["fwd3"], Xp).fit(cov_type="HAC", cov_kwds={"maxlags": XC_MAX})
    return {
        "anchor": anchor.strftime("%Y-%m"),
        "gap_mean": mean,
        "gap_last": float(gap.iloc[-1]),
        "gap_last_date": gap.index[-1].strftime("%Y-%m"),
        "gap_last_dev": float(dev.iloc[-1]),
        "gap_std": float(gap.std()),
        "reversion_lambda": lam,
        "reversion_lambda_t": float(mr.tvalues["dev_lag"]),
        "half_life_months": half_life,
        "adf_stat": float(adf[0]),
        "adf_pvalue": float(adf[1]),
        "predictor_beta": float(pred.params["dev"]),
        "predictor_t": float(pred.tvalues["dev"]),
        "predictor_r2": float(pred.rsquared),
        "_gap_series": gap,
        "_man_reb": man,
        "_cpi_reb": cpi,
    }


def fig_gap(lg: dict) -> Path:
    gap = lg["_gap_series"]
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True, gridspec_kw={"height_ratios": [2, 1]})
    axes[0].plot(lg["_man_reb"].index, lg["_man_reb"], color=C_WHOLE, lw=2, label="Manheim (wholesale, SA)")
    axes[0].plot(lg["_cpi_reb"].index, lg["_cpi_reb"], color=C_RETAIL, lw=2, label="CPI used (retail, SA)")
    axes[0].set_ylabel(f"Rebased 100 = {lg['anchor']}")
    axes[0].set_title("Retail vs wholesale levels and their cumulative gap")
    axes[0].legend(fontsize=9, loc="upper left")
    axes[1].plot(gap.index, gap, color="black", lw=1.8, label="gap = retail - wholesale")
    axes[1].axhline(lg["gap_mean"], color=C_ACC, lw=1.2, ls="--", label=f"mean {lg['gap_mean']:.1f}")
    axes[1].axhline(0, color="gray", lw=0.8)
    axes[1].fill_between(gap.index, lg["gap_mean"], gap, where=gap > lg["gap_mean"], color=C_RETAIL, alpha=0.15)
    axes[1].fill_between(gap.index, lg["gap_mean"], gap, where=gap < lg["gap_mean"], color=C_WHOLE, alpha=0.15)
    axes[1].set_ylabel("index pts")
    axes[1].legend(fontsize=9, loc="upper left")
    axes[1].set_title(f"Gap half-life ~ {lg['half_life_months']:.1f} mo | ADF p={lg['adf_pvalue']:.3f}")
    fig.tight_layout()
    p = HERE / "fig5_level_gap.png"
    fig.savefig(p)
    plt.close(fig)
    return p


# --------------------------------------------------------------------------- #
# (e) walk-forward nowcast + (integration) kernel comparison
# --------------------------------------------------------------------------- #
def _walk_forward(df: pd.DataFrame, manheim_lags: list[int], start: str,
                  use_persistence: bool = True, min_train: int = 48) -> pd.DataFrame:
    """Expanding-window OLS refit each month; predict CPI m/m.

    Leakage rule: to predict CPI used m/m for month t (released ~mid month t+1),
    the info set is Manheim finals through month t (published early t+1, before
    CPI) and CPI through month t-1. So regressors use Manheim lags k>=0 and the
    CPI persistence term uses y[t-1]; the model is fit only on months whose
    target y is already published (<= t-1).
    """
    d = pd.DataFrame(index=df.index)
    d["y"] = df[CPI_MOM]
    if use_persistence:
        d["y_lag1"] = df[CPI_MOM].shift(1)
    for k in manheim_lags:
        d[f"m{k}"] = df[MANHEIM_MOM].shift(k)
    xcols = ([f"m{k}" for k in manheim_lags] + (["y_lag1"] if use_persistence else []))
    d = d.dropna(subset=xcols)  # keep rows with full regressors; y may be NaN at the very end

    rows = []
    dates = d.index[d.index >= pd.Timestamp(start + "-01")]
    for t in dates:
        train = d.loc[d.index < t].dropna(subset=["y"])
        if len(train) < min_train:
            continue
        yt = d.loc[t, "y"]
        if pd.isna(yt):
            continue
        Xtr = sm.add_constant(train[xcols], has_constant="add")
        model = sm.OLS(train["y"], Xtr).fit()
        xt = np.concatenate([[1.0], d.loc[t, xcols].to_numpy(dtype=float)])
        pred = float(xt @ model.params.to_numpy())
        rows.append({"date": t, "actual": float(yt), "pred": pred})
    return pd.DataFrame(rows).set_index("date")


def _ar_benchmark(df: pd.DataFrame, start: str, order: int = 1, min_train: int = 48) -> pd.DataFrame:
    d = pd.DataFrame(index=df.index)
    d["y"] = df[CPI_MOM]
    for k in range(1, order + 1):
        d[f"y{k}"] = df[CPI_MOM].shift(k)
    xcols = [f"y{k}" for k in range(1, order + 1)]
    d = d.dropna(subset=xcols)
    rows = []
    for t in d.index[d.index >= pd.Timestamp(start + "-01")]:
        train = d.loc[d.index < t].dropna(subset=["y"])
        if len(train) < min_train:
            continue
        yt = d.loc[t, "y"]
        if pd.isna(yt):
            continue
        Xtr = sm.add_constant(train[xcols], has_constant="add")
        model = sm.OLS(train["y"], Xtr).fit()
        xt = np.concatenate([[1.0], d.loc[t, xcols].to_numpy(dtype=float)])
        rows.append({"date": t, "actual": float(yt), "pred": float(xt @ model.params.to_numpy())})
    return pd.DataFrame(rows).set_index("date")


def _metrics(pred: pd.DataFrame) -> dict:
    err = pred["pred"] - pred["actual"]
    hit = (np.sign(pred["pred"]) == np.sign(pred["actual"])).mean()
    return {
        "n": int(len(pred)),
        "mae": float(err.abs().mean()),
        "rmse": float(np.sqrt((err ** 2).mean())),
        "hit_rate": float(hit),
    }


def nowcast(df: pd.DataFrame) -> dict:
    man = _walk_forward(df, list(range(MAX_LAG + 1)), NOWCAST_START, use_persistence=True)
    ar1 = _ar_benchmark(df, NOWCAST_START, order=1)
    # align on common dates for a fair comparison
    common = man.index.intersection(ar1.index)
    man_c, ar_c = man.loc[common], ar1.loc[common]
    mm, ma = _metrics(man_c), _metrics(ar_c)
    return {
        "start": NOWCAST_START,
        "span": [common.min().strftime("%Y-%m"), common.max().strftime("%Y-%m")],
        "manheim_model": mm,
        "ar1_benchmark": ma,
        "mae_ratio_vs_ar": mm["mae"] / ma["mae"] if ma["mae"] else np.nan,
        "_pred": man_c,
        "_ar": ar_c,
    }


def integration_test(df: pd.DataFrame) -> dict:
    """Window-C (2022-01+) walk-forward: current [1,2] kernel vs estimated 0..4 kernel."""
    cur = _walk_forward(df, CURRENT_KERNEL_LAGS, WINDOW_C_START, use_persistence=True)
    new = _walk_forward(df, list(range(MAX_LAG + 1)), WINDOW_C_START, use_persistence=True)
    common = cur.index.intersection(new.index)
    cur_c, new_c = cur.loc[common], new.loc[common]
    mc, mn = _metrics(cur_c), _metrics(new_c)
    beats = mn["mae"] < mc["mae"]
    return {
        "window": "C",
        "window_start": WINDOW_C_START,
        "span": [common.min().strftime("%Y-%m"), common.max().strftime("%Y-%m")],
        "current_kernel_lags": CURRENT_KERNEL_LAGS,
        "candidate_kernel_lags": list(range(MAX_LAG + 1)),
        "current": mc,
        "candidate": mn,
        "candidate_beats_current": bool(beats),
        "mae_improvement_pct": float((mc["mae"] - mn["mae"]) / mc["mae"] * 100) if mc["mae"] else np.nan,
    }


def fig_nowcast(nc: dict) -> Path:
    pred = nc["_pred"]
    fig, ax = plt.subplots(figsize=(12, 5.2))
    ax.plot(pred.index, pred["actual"], color="black", lw=2, label="CPI used m/m (actual)")
    ax.plot(pred.index, pred["pred"], color=C_WHOLE, lw=1.8, ls="--", label="Manheim nowcast (walk-fwd)")
    ax.plot(nc["_ar"].index, nc["_ar"]["pred"], color=C_ACC, lw=1.2, alpha=0.7, label="AR(1) benchmark")
    ax.axhline(0, color="gray", lw=0.8)
    ax.set_ylabel("m/m %")
    ax.set_title(
        f"Walk-forward nowcast {nc['span'][0]}..{nc['span'][1]}  |  "
        f"MAE Manheim {nc['manheim_model']['mae']:.3f} vs AR1 {nc['ar1_benchmark']['mae']:.3f}  |  "
        f"hit {nc['manheim_model']['hit_rate']*100:.0f}%"
    )
    ax.legend(fontsize=9, ncol=3, loc="upper left")
    fig.tight_layout()
    p = HERE / "fig6_nowcast.png"
    fig.savefig(p)
    plt.close(fig)
    return p


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #
def main() -> dict:
    frame, meta = load()
    df = overlap(frame)
    anchor = pd.Timestamp("2015-01-01")

    figs = {}
    figs["levels"] = fig_levels(df, anchor).name
    figs["mom"] = fig_mom(df).name

    xc = xcorr_by_era(df)
    figs["xcorr"] = fig_xcorr(xc).name

    dl = dl_regression(df)
    asym = dl_asymmetry(df)
    figs["kernel"] = fig_kernel(dl).name

    lg = level_gap(df, anchor)
    figs["gap"] = fig_gap(lg).name
    lg_public = {k: v for k, v in lg.items() if not k.startswith("_")}

    nc = nowcast(df)
    figs["nowcast"] = fig_nowcast(nc).name
    nc_public = {k: v for k, v in nc.items() if not k.startswith("_")}

    integ = integration_test(df)

    # latest prints
    latest = {
        "date": df.index[-1].strftime("%Y-%m"),
        "manheim_mom": float(df[MANHEIM_MOM].iloc[-1]),
        "cpi_used_mom": float(df[CPI_MOM].iloc[-1]),
        "manheim_yoy": float(df["manheim_yoy"].iloc[-1]),
        "cpi_used_yoy": float(df["cpi_sa_yoy"].iloc[-1]),
    }

    results = {
        "meta": meta,
        "latest": latest,
        "xcorr": xc,
        "dl_regression": dl,
        "asymmetry": asym,
        "level_gap": lg_public,
        "nowcast": nc_public,
        "integration": integ,
        "figures": figs,
    }
    (HERE / "results.json").write_text(json.dumps(results, indent=2, default=_json_default), encoding="utf-8")

    # machine-readable kernel
    kernel = {
        "name": "used_vehicle_manheim_passthrough_kernel",
        "target": "CPI used cars & trucks SA m/m (CUSR0000SETA02)",
        "driver": "Manheim UVVI SA m/m (wholesale, mix/mileage-adjusted)",
        "estimated_on": dl["sample"],
        "n_obs": dl["n"],
        "manheim_lag_weights": dl["betas"],
        "manheim_lag_weights_se": dl["betas_se"],
        "persistence_rho": dl["persistence_rho"],
        "intercept": dl["intercept"],
        "cumulative_passthrough": dl["cumulative_passthrough"],
        "long_run_multiplier": dl["long_run_multiplier"],
        "r2": dl["r2"],
        "asymmetry": {
            "cum_up": asym["cum_passthrough_up"],
            "cum_down": asym["cum_passthrough_down"],
            "wald_equal_pvalue": asym["wald_equal_pvalue"],
        },
        "candidate_pass_through_lags": [int(k) for k in range(MAX_LAG + 1)],
        # what the model SHOULD use after the window-C test: candidate only if it wins,
        # otherwise the incumbent kernel is retained (no config change).
        "recommended_pass_through_lags": (
            [int(k) for k in range(MAX_LAG + 1)]
            if integ["candidate_beats_current"] else list(CURRENT_KERNEL_LAGS)
        ),
        "decision": ("adopt_candidate" if integ["candidate_beats_current"] else "keep_incumbent_no_change"),
        "integration_window_C": {
            "candidate_beats_current": integ["candidate_beats_current"],
            "current_mae": integ["current"]["mae"],
            "candidate_mae": integ["candidate"]["mae"],
            "mae_improvement_pct": integ["mae_improvement_pct"],
        },
        "provenance": meta["manheim_provenance"],
        "note": "Manheim UVVI is seasonally adjusted and mix/mileage-adjusted; "
                "compared against BLS SA used-cars CPI. Weights are HAC (Newey-West) OLS betas.",
    }
    (HERE / "lag_weights.json").write_text(json.dumps(kernel, indent=2, default=_json_default), encoding="utf-8")

    print(json.dumps({"latest": latest,
                      "dl": {"cum": dl["cumulative_passthrough"], "rho": dl["persistence_rho"], "r2": dl["r2"]},
                      "asym": {"up": asym["cum_passthrough_up"], "down": asym["cum_passthrough_down"],
                               "p": asym["wald_equal_pvalue"]},
                      "nowcast": nc_public,
                      "integration": {k: integ[k] for k in ("current", "candidate", "candidate_beats_current", "mae_improvement_pct")},
                      "xcorr_peaks": {e: (r["peak_lag"], r["peak_corr"]) for e, r in xc.items()}},
                     indent=2, default=_json_default))
    return results


def _json_default(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(str(type(o)))


if __name__ == "__main__":
    main()
