# Used-vehicle pass-through: Manheim (wholesale) → BLS CPI used cars & trucks (retail)

*Generated 2026-07-07 from live data. Overlap sample 1997-01 → 2026-05.*

## TL;DR

- **Manheim leads CPI by ~2 months.** Full-sample cross-correlation peaks at **lag 2** (r=0.50); the distributed-lag kernel puts its largest, most significant weight on **lag 2** (β=0.207, t=3.6) plus a contemporaneous lag-0 term (β=0.125, t=2.5).
- **Retail damps wholesale hard.** Cumulative pass-through (Σ Manheim betas, lags 0–4) = **0.40** — i.e. a 1 pp wholesale m/m move maps to ~40 bp of retail CPI m/m over the following quarter (β≪1, same amplitude story as ZORI→shelter). With CPI persistence (ρ=0.47) the long-run multiplier is 0.76. Model R²=0.47.
- **No statistically significant up/down asymmetry** over the full sample (cum-up 0.41 vs cum-down 0.39, Wald p=0.88). The *shape* hints that downward pass-through is more drawn out (more weight at lag 4), but the difference is not significant.
- **The retail–wholesale gap does NOT reliably mean-revert** (ADF p=0.89, half-life ≈ 88 mo). It is best treated as a slow-drifting, near-non-stationary spread; its predictive content when stretched is weak (t=-2.0, R²=0.07).
- **Nowcast beats a naïve AR(1) on error** (2019-01→2026-05): MAE 1.164 vs 1.242 pp (6% lower), but not on sign (hit 65% vs 69%).
- **Integration decision: no change.** The richer lag-0…4 kernel does **not** beat the model's current `[1, 2]` kernel in window-C walk-forward (MAE 0.904 vs 0.840; 7.6% worse). Config left unchanged.

## Data & provenance

- **Manheim Used Vehicle Value Index (UVVI)** — 353 monthly obs, **1997-01 → 2026-05**. Source: live Cox XLSX (https://www.coxautoinc.com/wp-content/uploads/2026/06/May-2026-Manheim-Used-Vehicle-Value-Index.xlsx). The published series is **seasonally adjusted and mix/mileage-adjusted** (base **Jan 1997 = 100**). Note: the true history starts **1997-01**, not 1995 — the workbook's own column is labelled "Index (1/97 = 100)". We use the SA level as the primary series to match the SA CPI.
- **BLS CPI used cars & trucks** — `CUSR0000SETA02` (SA, primary) and `CUUR0000SETA02` (NSA, reference only), pulled via the BLS API v2. SA history 1953-01 → 2026-05.
- **Overlap used for all analysis:** 1997-01 → 2026-05.
- Latest prints (2026-05): Manheim m/m **0.32%** (YoY 3.6%); CPI used m/m **0.10%** (YoY -2.0%). *Wholesale is running hotter than retail YoY right now — a divergence the gap section addresses.*

Reproduce: `python uv_data.py` (rebuilds cached CSVs) → `python run_analysis.py` (figures + `results.json` + `lag_weights.json`) → `python write_report.py` (this file). If the Manheim pull ever fails, `uv_data.py` stops loudly and prints exactly what to paste into `data/manual/manheim_uvvi.csv`; it never fabricates values.

## (a) Levels & m/m overlays

![Rebased levels](fig1_levels_rebased.png)

![m/m overlay](fig2_mom_overlay.png)

Rebased to Jan-2015 = 100, wholesale and retail track loosely pre-COVID, then wholesale spikes far above retail in 2021 and remains elevated. The m/m panels show Manheim is much more volatile than CPI — retail smooths and damps the wholesale signal.

## (b) Cross-correlation by era (Manheim leads CPI by k months)

![Cross-correlation by era](fig3_xcorr_by_era.png)

| Era | n | peak lead (months) | peak corr |
|---|---:|---:|---:|
| pre-2020 | 276 | 4 | 0.33 |
| COVID 2020-2022 | 36 | 2 | 0.72 |
| post-2022 | 41 | 3 | 0.64 |
| full | 353 | 2 | 0.50 |

The expected 1–2 month lead is clearest in the **COVID shock** (peak lag 2, r=0.72) and **post-2022** (lag 3, r=0.64). **Pre-2020** the relationship is weak and noisy (peak lag 4, r=0.33 only) — in calm markets retail used-car CPI is driven as much by its own seasonality/mix as by wholesale. The pandemic episode dominates the full-sample correlation, so read the kernel below as a blend, not a stable structural constant.

## (c) Distributed-lag pass-through kernel

![Fitted lag kernel](fig4_lag_kernel.png)

OLS with Newey–West (HAC, maxlags 6) SEs, n=348, sample 1997-06→2026-05:

`CPI_used_SA_mm[t] = c + Σ_{k=0..4} β_k · Manheim_mm[t−k] + ρ · CPI_used_SA_mm[t−1] + e`

| term | estimate | HAC SE | t |
|---|---:|---:|---:|
| Manheim lag 0 (β0) | 0.125 | 0.050 | 2.5 |
| Manheim lag 1 (β1) | 0.048 | 0.049 | 1.0 |
| Manheim lag 2 (β2) | 0.207 | 0.057 | 3.6 |
| Manheim lag 3 (β3) | 0.042 | 0.038 | 1.1 |
| Manheim lag 4 (β4) | -0.023 | 0.034 | -0.7 |
| persistence ρ | 0.471 | 0.075 | 6.3 |
| intercept | -0.064 | — | — |

- **Cumulative pass-through (Σβ, lags 0–4) = 0.400.** Only lag-0 and lag-2 are individually significant; lags 1, 3, 4 are ~0.
- **Long-run multiplier = Σβ/(1−ρ) = 0.757** — accounting for CPI's own momentum, a sustained 1 pp wholesale shift eventually moves retail m/m by ~0.76 pp.
- **R² = 0.474** (adj 0.465). β≪1 confirms retail heavily damps wholesale.

### Asymmetric up/down test

Splitting Manheim m/m into positive and negative parts across the same lags:

- cumulative **up** pass-through = 0.405
- cumulative **down** pass-through = 0.386
- Wald test of equality: **p = 0.876** → cannot reject symmetry.

The prior — *retail follows auction prices down more slowly* — is **directionally visible** (down-side weight leaks to lag 4: β_dn4=0.091 vs β_up4=-0.110) but is **not statistically significant** over 1997–2026. Don't hard-code an asymmetric kernel on this evidence.

## (d) Level-gap: retail vs wholesale divergence

![Level gap](fig5_level_gap.png)

Gap = CPI-retail − Manheim-wholesale (both rebased Jan-2015 = 100). Mean 1.5, sd 19.4. Latest (2026-05): **-31.3** (-32.8 vs mean ≈ -1.7 sd) — retail sits well **below** wholesale on the 2015 basis, i.e. wholesale cumulated more since 2015 and retail has not fully caught up/down.

- **Mean reversion is weak-to-absent.** Δgap on lagged gap-deviation gives λ=-0.008 (t=-1.1), implied half-life ≈ **88 months**. ADF on the gap: stat -0.51, **p=0.89** → cannot reject a unit root. Treat the spread as near-non-stationary.
- **Spread-as-predictor is weak.** Regressing next-3-month cumulative CPI m/m on the current gap deviation gives β=-0.043 (t=-2.0), R²=0.07. The sign is right (stretched-high retail → softer future retail) and marginally significant, but given the non-stationarity this is a caution flag, not a tradable signal.

## (e) Walk-forward nowcast

![Nowcast](fig6_nowcast.png)

**Leakage rule:** to nowcast CPI used m/m for month *t* (released ~mid-month *t+1*), the info set is Manheim *finals* through month *t* (published in the first days of *t+1*, ahead of CPI) plus CPI through *t−1*. The kernel is refit on an expanding window each month; nothing from month *t* CPI or later enters the fit.

> Caveat: the public UVVI workbook is the **month-end final** only. Manheim also publishes a > mid-month *flash*, but no free archive of past flash prints exists, so this test uses the > month-end final (which still lands before the CPI release). Wiring in the live mid-month flash > would only *add* timeliness, so these numbers are a conservative floor.

| model | n | MAE (pp) | RMSE (pp) | sign hit-rate |
|---|---:|---:|---:|---:|
| Manheim kernel (lags 0–4 + persistence) | 89 | 1.164 | 1.795 | 65% |
| AR(1) benchmark | 89 | 1.242 | 1.897 | 69% |

Over 2019-01→2026-05 the Manheim nowcast cuts MAE by **6%** vs AR(1), but its sign hit-rate is slightly *lower*. Net: Manheim helps most on **magnitude and turning-point timing**, less on calling the sign of small months — consistent with a damped-amplitude, ~2-month-lead lead indicator.

## Integration decision (Tier-1 used-vehicle model)

The Tier-1 `SETA02` model (`cpi_model/triage.py`) currently declares `pass_through_lags = [1, 2]`. I compared that lag support against the estimated lag-0…4 kernel **out-of-sample in backtest window C** (2022-01→2026-05, the window C start `2022-01` from `cpi_model/backtest.py`), both refit walk-forward with the same persistence term so the comparison isolates the Manheim lag structure:

| kernel | lags | walk-fwd MAE (pp) | RMSE | hit |
|---|---|---:|---:|---:|
| **current** | [1, 2] | **0.840** | 1.183 | 70% |
| candidate | [0, 1, 2, 3, 4] | 0.904 | 1.231 | 70% |

The candidate **does not beat** the current kernel (0.904 vs 0.840 MAE, -7.6% worse). 
Per the brief, since it does not beat the incumbent in window C, **no config is changed**. The parsimonious `[1, 2]` kernel generalizes better here: the extra lag-0/3/4 parameters are ~0 in the full-sample fit and cost degrees of freedom on the short (~53-month) window-C sample. The lag-2-centred story is fully consistent with the incumbent — the analysis *validates* the current kernel rather than replacing it.

The full fitted kernel (weights, SEs, cumulative/long-run pass-through, asymmetry, and this window-C comparison) is written machine-readably to [`lag_weights.json`](lag_weights.json).

## Caveats

- The 2020–2022 chip-shortage spike dominates the full-sample fit; pre-2020 the wholesale→retail link is weak (see era table). The kernel is a blend across regimes, not a structural constant.
- Manheim UVVI is SA **and** mix/mileage-adjusted; CPI used is SA but constructed differently (retail transaction sampling, its own seasonal factors). Treat Manheim as a damped-amplitude, ~2-month **timing/direction** lead (β≈0.4 cumulative), not a 1:1 predictor.
- The retail–wholesale gap is near-non-stationary over 1997–2026; do not assume it snaps back on a fixed schedule.
- History starts 1997-01 (Manheim base), so pre-1997 CPI used-car history (available back to 1953) has no wholesale counterpart and is excluded from the joint analysis.

