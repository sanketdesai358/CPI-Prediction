# Claude Code prompt — CPI Used Cars vs. Manheim Used Vehicle Value Index (lag analysis)

Replicate the shelter/ZORI lag study, but for **used vehicles**. Reuse the pattern in
`cpi-model/outputs/shelter_zori_lag/shelter_plots.py` (BLS pull → transform → lag sweep →
figures). Do NOT fabricate, guess, or hardcode-from-memory any index value. If a data
source can't be reached, FAIL LOUDLY and print the exact manual steps for me.

## Goal
Find the lag at which the **Manheim Used Vehicle Value Index (MUVVI)** best leads the
**CPI used cars & trucks** component, historically. Manheim is a *wholesale auction* index
and is expected to lead the *retail* CPI by roughly **1–2 months**, so this is a
short-lag, month-over-month analysis (not the 15-month YoY relationship from shelter).

## Data

### 1. CPI used cars & trucks (BLS — automated, key already in repo `.env`)
- Seasonally adjusted index: `CUSR0000SETA02`
- Non-seasonally adjusted (backup): `CUUR0000SETA02`
- Pull via the existing BLS API v2 client pattern (`BLS_API_KEY` from repo-root `.env`),
  2015–present. Guard against `"-"` / `"(NA)"` placeholder values (as in `shelter_plots.py`).

### 2. Manheim Used Vehicle Value Index (MUVVI — PROPRIETARY, no free bulk feed)
The index is published monthly by Cox Automotive/Manheim; base Jan 1995 = 100; both a
**seasonally adjusted (SA)** and NSA series exist. There is **no free API or bulk CSV**
(it is NOT on FRED). Sourcing options, in order of preference:

1. **Maintained local CSV** at `cpi-model/data/manheim/manheim_muvvi.csv` with schema:
   `date,index_sa,index_nsa,mom_sa_pct` (one row per month, `date` = month-start `YYYY-MM-01`).
   If this file exists, load it and use it as the source of truth.
2. **If the CSV is missing or stale**, attempt to pull the monthly values and MoM % from:
   - Cox Automotive / Manheim newsroom monthly releases
     (`https://www.coxautoinc.com/newsroom/` — search "Manheim Used Vehicle Value Index"),
     which state the index level and the SA month-over-month % each month; and/or
   - Trading Economics MoM page: `https://tradingeconomics.com/united-states/used-car-prices-mom`
     (recent history + MoM; scraping may be blocked — send a real User-Agent, and if it
     returns non-200 or a challenge page, do NOT scrape around it).
   Write whatever you successfully retrieve into `manheim_muvvi.csv` and print the rows
   added so I can eyeball them.
3. **If neither works**, STOP and tell me exactly which URLs failed and what to paste in
   (a monthly MUVVI SA level + MoM series back to 2015), then wait.

**Never invent index values.** A partial-but-real series is fine; a fabricated one is not.

## Transforms
- Primary comparison: **month-over-month % change** of both series (SA versions).
  - CPI used cars MoM = `CUSR0000SETA02.pct_change()*100`.
  - Manheim MoM = SA index `pct_change()*100` (or the reported `mom_sa_pct` if that's what
    the source gives).
- Secondary: **3-month annualized** and **YoY %** for robustness.

## Lag sweep
- Sweep k = 0 … 6 months with Manheim LEADING CPI: correlate `CPI_MoM[t]` vs
  `Manheim_MoM[t-k]`. Report the best k and the correlation neighborhood (k-2 … k+2).
- Repeat for the 3-mo-annualized and YoY transforms; note whether the best lag is stable
  across transforms (it should land around 1–2 months for MoM).
- Also fit a simple OLS at the best lag (`CPI_MoM ~ β·Manheim_MoM_lagged + c`) and report
  β and R² — Manheim swings are larger than CPI's, so expect **β < 1** (retail damps
  wholesale), same amplitude story as ZORI→shelter.

## Outputs (mirror the shelter study)
Save everything to `cpi-model/outputs/usedcar_manheim_lag/`:
- `fig1_lag_correlation.png` — correlation vs. lag (mark the best k, shade the plausible band).
- `fig2_overlay_shifted.png` — CPI used cars MoM vs. Manheim MoM shifted by best k.
- `fig3_overlay_raw.png` — unshifted overlay (shows Manheim turning first).
- `usedcar_manheim.csv` — merged monthly series (levels + MoM + YoY for both).
- `usedcar_manheim_plots.py` — the reproducible script.
- Print a short results summary to stdout: best lag per transform, peak corr, OLS β/R²,
  latest MoM and YoY values for both series with their as-of dates.

## Caveats to print with the results
- The 2020–2022 chip-shortage spike dominates the correlation; report the best lag on the
  full sample AND on a pre-2020 sub-sample so I can see how much the pandemic episode drives it.
- CPI used cars is SA and already smoothed vs. wholesale; treat Manheim as a **timing/direction**
  lead with a damped magnitude (β < 1), not a 1:1 predictor.
- Manheim publishes a mid-month "flash" estimate too; use the **full-month final** value only,
  and record the publication timing if you plan to wire this into a real-time feed later.
