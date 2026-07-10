# STEO vs BLS electricity — can STEO's residential price drive the SEHF01 nowcast?

**Analyst run:** 2026-07-10 · analysis only, production model untouched.
**Verdict up front: REJECT.** STEO's nominal residential electricity price is the
**worst** of every method tested as a same‑month CPI nowcast, it does **not** beat a
trivial seasonal baseline at any forward horizon (t+1…t+3), and when given optimal
walk‑forward weight alongside either the incumbent model or a seasonal AR it receives
a coefficient of ≈ **−0.02** and adds **0.0** MAE value. Details and the (not‑recommended)
feed spec below.

---

## 1. Data

| Series | Source | Coverage | Use |
|---|---|---|---|
| STEO residential price, **nominal** (`ESRCUUS`, cents/kWh, monthly) | EIA APIv2 `steo` dataset (current vintage) | 1976‑07 → 2027‑12 | Part a (levels/alignment, in‑sample) |
| STEO **real‑time vintages** (`ESRCUUS`) | 139 archived issues `archives/{mon}{yy}_base.xlsx` | issues **2015‑01 → 2026‑07** | Parts b, c (honest tests) |
| CPI electricity **NSA** `CUUR0000SEHF01`, **SA** `CUSR0000SEHF01` | BLS APIv2 | 2000‑01 → 2026‑05 | target + SA offset |
| Henry Hub spot (daily→monthly avg) | cached EIA feed `henry_hub.json` | 2006‑09 → present | baseline (iii) |

I deliberately used the **nominal** STEO series, not the "real" (CPI‑deflated) series on
the *realprices* page — the real series is deflated by the CPI and would be circular
against a CPI target.

**Vintage integrity (the honest part).** Each `_base.xlsx` is the STEO data workbook *as
published* that month, so the `ESRCUUS` path it contains is a genuine real‑time
forecast — no revision leakage. I keyed every vintage by its **issue month from the
filename** (unambiguous), located `ESRCUUS` by scanning column A of every sheet
(robust to STEO's table‑renumbering over the years — it resolved to `2tab` for all 139),
and mapped values from the "Table Beginning Month" in the workbook's `Dates` sheet.
Because EIA retail‑price actuals lag ~2 months, the value a month‑`t` issue prints for
month `t` is a true forecast, not a revised actual. **Full monthly real‑time coverage
2015‑01 → 2026‑07 (139 consecutive issues, no gaps).**

Scripts: [`fetch_steo_vintages.py`](fetch_steo_vintages.py) (archive puller/parser),
[`analyze.py`](analyze.py) (all analysis), raw pulls in [`raw/`](raw/), machine‑readable
numbers in [`results.json`](results.json).

---

## 2. Part a — Levels & alignment (2015–present)

STEO price and CPI electricity measure **similar but not identical** things:

- **STEO `ESRCUUS`** = average **revenue per kWh** (total residential revenue ÷ kWh sold).
  It moves with the **usage mix** (weather‑driven consumption shifting customers across
  tiered/seasonal rate blocks) and is model‑smoothed at monthly frequency.
- **CPI `SEHF01`** = a **fixed‑quantity tariff index** — it prices a constant consumption
  basket, stripping out the usage‑mix effect by construction.

**Quantifying the gap** (`ESRCUUS` current vintage vs CPI NSA, 2015‑01→2026‑05, n=135):

| Metric | Value |
|---|---|
| Correlation of m/m | **0.18** |
| OLS slope (CPI m/m on STEO m/m) | 0.13 |
| MAE between the two m/m series | **1.89 pp** |
| Mean m/m (STEO / CPI) | 0.344% / 0.318% |
| Cumulative growth 2015‑01→2026‑05 (STEO / CPI) | **+52.7% / +47.6%** |

So on **trend** the two are close (STEO runs ~5 pts hotter over a decade — exactly the
usage‑mix wedge you'd expect from average‑revenue vs fixed‑basket). But on a
**month‑to‑month** basis they barely comove (r = 0.18). The m/m overlay
([`fig_a2_mm_overlay.png`](fig_a2_mm_overlay.png)) shows why: the two series have
**offset seasonal phases** — STEO's revenue/kWh peaks and troughs land in different
months than CPI's tariff seasonal. That phase mismatch is the whole story of Parts b–c.

Figures: [`fig_a1_levels_overlay.png`](fig_a1_levels_overlay.png) (indexed levels),
[`fig_a2_mm_overlay.png`](fig_a2_mm_overlay.png) (m/m overlay),
[`fig_a3_scatter.png`](fig_a3_scatter.png) (scatter + fit).

---

## 3. Part b — Honest nowcast test (the money question)

**Target:** CPI electricity **NSA m/m** for month `t`.
**STEO predictor:** the m/m implied by the vintage **issued in month `t`** (`ESRCUUS[t]/ESRCUUS[t‑1]−1`,
both legs from the same issue). This is strictly ex‑ante — that issue is released ~2nd
week of month `t`, roughly **four weeks before** the CPI print for month `t` (mid‑`t+1`).
All baselines are strictly causal (expanding window, data `< t` only).

### 3a. Same‑month nowcast — common sample 2016‑01…2026‑05 (n=122)

| Method | MAE (pp) | RMSE | corr | bias |
|---|---|---|---|---|
| **STEO nowcast (issue = t)** | **1.945** | 2.379 | 0.12 | −0.19 |
| (i) Production model `0.55·last + 0.30·mean₃ + 0.15·seasonal` | 1.051 | 1.319 | 0.44 | −0.02 |
| (ii) Seasonal AR(1) (deseasonalized, φ=0.18) | **0.817** | 1.152 | **0.84** | −0.01 |
| (iii) Henry Hub distributed lag (0–6 mo) | 1.076 | 1.487 | −0.08 | −0.13 |

STEO is **2.4× worse** than the seasonal AR and clearly worse than the incumbent
production model. CPI electricity NSA m/m is ~85% a stable seasonal wave (June
**+4.9%**, October **−3.4%**, Jan +1.4%, May +1.6%, Nov −1.7%), which the seasonal AR
nails and STEO's mis‑phased revenue seasonal actively fights.
See [`fig_b1_nowcast_mae.png`](fig_b1_nowcast_mae.png), [`fig_b2_steo_scatter.png`](fig_b2_steo_scatter.png).

**Vintage‑timing sensitivity** (STEO's own availability span, n≈135):

| STEO vintage used | MAE | corr | note |
|---|---|---|---|
| issue = t (≈4‑wk lead) — recommended honest choice | 1.97 | 0.16 | pure forecast |
| issue = t−1 (1‑mo‑ahead) | 1.88 | 0.18 | — |
| issue = t+1 (freshest, ~days before print) | 1.95 | 0.15 | month t now near‑actual; still no better |

Even the *freshest* vintage available before the print does not rescue it.

### 3b. Forward horizons t+1…t+3 — does STEO extend our electricity horizon?

From each issue `M`, STEO's forecast m/m for `M+h` vs actual CPI m/m, compared to a
seasonal baseline known at `M`:

| Horizon h | STEO MAE | Seasonal MAE | STEO corr | Seasonal corr |
|---|---|---|---|---|
| 0 | 1.97 | **0.83** | 0.16 | 0.85 |
| 1 | 1.88 | **0.83** | 0.18 | 0.85 |
| 2 | 1.92 | **0.83** | 0.13 | 0.85 |
| 3 | 1.92 | **0.83** | 0.15 | 0.85 |

**STEO loses to a naive seasonal mean at every horizon.** It does **not** extend the
horizon. ([`fig_b3_horizon_mae.png`](fig_b3_horizon_mae.png).) The flat STEO line across
h is itself the tell: STEO carries essentially no month‑specific information that a
calendar‑month average doesn't already have.

### 3c. Is there *any* signal? Deseasonalized innovation test

Correlating STEO's innovation (m/m minus its own causal same‑month mean) against CPI's
innovation isolates non‑seasonal content: **r = 0.24 (n=111)**. A faint positive whisper
— but, as Part c shows, it does not survive out‑of‑sample.

---

## 4. Part c — Combination test (walk‑forward window C, 2022‑01+)

Expanding‑OLS, refit every month. The honest question is STEO's **marginal** value, so I
compare each `base + STEO` combo against a **recalibrated base‑only** control (same
intercept+slope OLS, base feature only) — comparing to the *raw* base would wrongly
credit STEO with the recalibration gain.

| Model (window C, n≈51) | MAE (pp) | corr |
|---|---|---|
| Production alone (raw) | 1.222 | 0.24 |
| Seasonal AR alone (raw) | 0.927 | 0.74 |
| STEO nowcast alone | 2.198 | 0.05 |
| Production recalibrated (1+prod) | 1.100 | — |
| **Production + STEO** | 1.119 | 0.19 |
| Seasonal AR recalibrated (1+sar) | **0.765** | — |
| **Seasonal AR + STEO** | 0.764 | — |

**Marginal value of adding STEO** = MAE(recalibrated base) − MAE(base + STEO):

| Base | recal‑only MAE | + STEO MAE | **Δ from STEO** | STEO β |
|---|---|---|---|---|
| Production | 1.100 | 1.119 | **−0.019 (worse)** | +0.021 |
| Seasonal AR (champion) | 0.765 | 0.764 | **+0.0006 (nil)** | **−0.021** |

The entire apparent gain over the "raw" baselines is **recalibration**, not STEO:
seasonal AR improves 0.927→0.765 by re‑estimating its own coefficient; adding STEO on
top of that moves MAE by six ten‑thousandths of a point, with a **negative** weight.
STEO's β in the production combo (avg 0.021, last 0.014) is likewise a rounding error.
[`fig_c1_combo_series.png`](fig_c1_combo_series.png).

**Fitted coefficients (for the record):**
- Production+STEO walk‑fwd β (avg): intercept 0.114, production **0.576**, STEO **0.021**.
- Seasonal AR+STEO walk‑fwd β (avg): intercept 0.089, seasonal‑AR **0.606**, STEO **−0.021**.
- Seasonal AR(1) φ (deseasonalized, full sample): **0.181**.
- Henry Hub distributed lag β [const, lag0…lag6]: 0.292, 0.010, 0.009, 0.006, 0.000, 0.003, 0.001, 0.007 — pass‑through ~0.04pp per 1% HH move, and negative out‑of‑sample corr (the constant does the work).

---

## 5. Verdict

**Reject STEO's residential price as the SEHF01 nowcast driver, and reject it as a
t+1…t+3 forward signal.** Across a clean 2015–2026 real‑time backtest (139 archived
vintages, zero revision leakage), STEO is the worst same‑month nowcast tested
(MAE 1.95 vs 0.82 for a plain seasonal AR and 1.05 for the incumbent), fails to beat a
calendar‑month average at every forward horizon, and contributes ≈ 0 (β ≈ −0.02) when
optimally combined with either the production model or the seasonal AR. The root cause
is structural, not a tuning issue: `ESRCUUS` is **average revenue per kWh**, whose
usage‑mix‑driven seasonal is **phase‑shifted** relative to CPI's fixed‑quantity tariff
seasonal, so its monthly moves are close to orthogonal to what `SEHF01` does (m/m
r ≈ 0.12–0.18). The only positive is a faint deseasonalized‑innovation correlation
(r ≈ 0.24) that does not survive out‑of‑sample.

**Actionable takeaway for the pending SEHF01 rework:** the incumbent
`0.55·last+0.30·mean₃+0.15·seasonal` blend is already beaten — not by STEO, but by a
**deseasonalized seasonal AR(1)** (MAE 0.82 vs 1.05, r 0.84 vs 0.44). That, not STEO, is
the upgrade worth pursuing for the electricity nowcast. STEO should **not** be wired in.

### Feed spec — *for reference only; adoption not recommended*
If a future override still wants STEO as a forward‑only overlay, the leakage‑safe spec is:
- **Series:** EIA APIv2 `steo` dataset, `seriesId = ESRCUUS` (nominal cents/kWh, monthly). *Never* the real/deflated series.
- **Vintage handling:** for a target month `t`, use only the issue with `issue_month ≤ t`
  (the month‑`t` issue gives ~4 weeks of lead before the CPI print). Never pull the
  current‑vintage API series into a backtest — it is fully revised and in‑sample.
- **Publication timing:** STEO releases ~2nd week of each month; the CPI print lands
  ~mid‑`t+1`. Enforce `steo_issue_date < cpi_release_date` in any backtest; the
  month‑`t` issue satisfies this with a comfortable margin, the month‑`t+1` issue only
  by a few days (and offers no accuracy gain).
- **Signal, if used at all:** the **deseasonalized innovation** (STEO m/m minus its own
  same‑month mean), *not* raw STEO m/m — raw m/m injects the wrong seasonal phase.

---
*Reproduce:* `python fetch_steo_vintages.py` then `python analyze.py` from this folder
(requires `EIA_API_KEY`, `BLS_API_KEY` in `../../../.env`; `openpyxl`, `pandas`, `numpy`, `matplotlib`).
