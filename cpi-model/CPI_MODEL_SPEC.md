# CPI Forecast Model Spec — Component-Level m/m Nowcast

**Goal.** A monthly model that forecasts the next unpublished CPI-U reference month at the **item-stratum level** (m/m NSA), aggregates bottom-up with relative-importance weights to headline and core m/m, applies published seasonal factors to produce SA m/m, and converts to y/y. Companion documents: `CPI_FORECAST_SPEC.md` (data layer, sources, series grammar — reuse sections 1–4 verbatim) and the validated `registry.json` from the `cpi-excel` build (component catalog; this spec extends it).

**Design principle (non-negotiable).** Model each component the way BLS *actually calculates it*. Components whose BLS input data is externally observable are forecast from **the actual input** (measurement models). Components that are survey-based and persistence-driven are forecast with **statistical trend models**, with model complexity scaled to volatility. Nothing is forecast at the headline level; headline is an accounting identity over component forecasts.

---

## 1. Forecast identity and target definition

Target: for forecast month *t* (the next unpublished reference month), forecast NSA m/m for every stratum *i*:

```
r_i,t = I_i,t / I_i,t-1 − 1                     (NSA, stratum level — the atomic forecast)

Headline NSA m/m:   R_t = Σ_i  RI_i,t−1 × r_i,t / 100
Headline NSA y/y:   Y_t = I_t / I_t−12 − 1     (11 of 12 months already known → y/y is fully
                                                determined by the m/m forecast; report base effects)
```

**Seasonal adjustment is deterministic, not forecast.** BLS publishes each year's seasonal factors in February and applies them unchanged all year (2025-derived factors apply to 2026 data). So: forecast NSA → multiply by the published factor from the Seasonal Factors XLSX → SA stratum m/m → aggregate SA using BLS's *components-for-seasonal-aggregation* structure (SA aggregates are built from intermediate aggregates, not raw strata — replicate this, don't hand-sum). This removes an entire error source most naive models get wrong.

**Weights.** RI_i,t−1 = December RI price-updated to t−1 per the BLS formula (`CPI_FORECAST_SPEC.md` §4). January forecasts must use the *new* weight vintage (pull the weight-update comparison page) — a known step-risk each year.

---

## 2. Component triage — four tiers

Every stratum gets a `tier` assignment in the extended registry. Roughly 40 named strata (≈80% of weight) are hand-assigned below; the long tail is auto-triaged by the decision rule in §4.

### Tier 1 — Measurement models (~20% of weight; most of headline volatility)
BLS's input is externally observable at higher frequency. Forecast = pass-through regression from the actual input, aligned to BLS timing, plus a small residual AR term.

```
r_i,t = α_i + Σ_k β_i,k · x_i,t^(k) + φ_i·ε_i,t−1 + ε_i,t
```
where x are input-series changes aggregated to **BLS pricing-period averages** (three ~10-day windows; gasoline uses full-month secondary-source data, so use the full-month average of daily prices vs. prior full month). Estimate β on ≥10 years of history; expect β≈1 for gasoline, <1 with distributed lags elsewhere.

| Stratum | Code | Input (the actual driver) | Notes |
|---|---|---|---|
| Gasoline (all types) | SETB01 | EIA weekly retail (free) / OPIS-AAA daily → monthly avg of daily prices | BLS uses full-month secondary data since Jun-2021; this is the closest thing to a solved component — target R² > 0.95 on m/m |
| Fuel oil | SEHE01 | EIA heating oil retail | seasonal demand overlay |
| Utility piped gas | SEHF02 | Henry Hub with 1–3 mo distributed lag + tariff filings | modified Laspeyres; regulated pass-through is slow |
| Electricity | SEHF01 | State tariff filing calendar + EIA retail price | mostly Tier-2-like steps; treat filings as events |
| Used cars & trucks | SETA02 | Manheim UVVI (mid-month release), Black Book | leads CPI 1–2 months; estimate the lag kernel, include depreciation/QA wedge as a slow drift term |
| New vehicles | SETA01 | J.D. Power PIN if licensed; else ATP/incentive proxies (Cox/KBB), inventory days-supply | include Sept–Nov model-year changeover dummies (class-mean imputation + resource-cost QA make raw ATP ≠ CPI) |
| Airline fares | SETG01 | ARC ticketing if licensed; else jet fuel + web-fare scrape + capacity | directional fare-mix rules make this noisy; keep residual AR |
| Food-at-home commodity strata (eggs SEFH?, beef, milk, coffee…) | SAF11 children | USDA retail/wholesale, futures (live cattle, wheat, corn, coffee) with 1–2 mo pass-through | only where a liquid wholesale price exists; otherwise Tier 3 |
| Car & truck rental | SETA04 | daily rental rate scrapes | small weight, high vol |

### Tier 2 — Structural / mechanical models (~40% of weight; shelter dominates)
The BLS estimator itself is the model — a known transformation of a latent input. Do not fit generic time-series here; encode the mechanics.

| Stratum | Code | Mechanics to encode | Model |
|---|---|---|---|
| Rent of primary residence | SEHA | 6 rotating panels; monthly link = 6th root of quality-adjusted 6-month relative; age-bias adjustment | State-space: latent market-rent growth g_t observed via new-tenant indexes (ZORI, Apartment List, BLS/Cleveland-Fed NTRI) and all-tenant proxies; CPI rent m/m ≈ moving average of g over trailing ~6–18 months (estimate the kernel; literature: new-tenant rents lead 3–6 quarters). Initialize kernel ≈ uniform 6-month smoother × renewal-share damping |
| Owners' equivalent rent | SEHC | Same sample, owner-stock reweighting; utilities stripped | Same latent factor as rent with its own loading + spread state (rent–OER gap mean-reverts) |
| Health insurance | SEME | Retained-earnings method: lagged insurer financials incorporated on a semiannual schedule | Deterministic drift between incorporation dates + forecastable step at each reset (estimate from insurer MLR data); verify current cadence on the factsheet |
| College tuition & fees | SEEB01 | Sticker-price repricing concentrated in Aug–Sep (academic year) | Seasonal event model: Aug/Sep carries ~all of the annual change (use announced tuition data); near-zero other months (NSA) |
| Motor vehicle insurance | SETE | Filed premium changes; carry-forward between filings | Momentum model on filing trackers (S&P Global rate-filing data if licensed; else strong AR with level shifts) |
| Water/sewer/trash | SEHG | Municipal fee schedules, Jan/Jul resets | Calendar-step model |
| Cable/satellite, wireless | SEED03 etc. | Wireless: secondary plan-offer data + hedonic imputation since Jul-2025 | Plan-launch event tracking; hedonic churn shows up as step-downs at launches |

### Tier 3 — Statistical trend models (~35% of weight; the persistent survey-based core)
Survey-collected, no observable external input, low-to-moderate volatility, high persistence — exactly the user's "trend analysis" bucket. Per-stratum model selected by statistical profile (§4):

- **Low vol, high persistence** (most core services: personal care services, household operations, repair services, medical services strata, recreation services, education ex-tuition): seasonal AR — regress NSA m/m on own lags (1,2,12) + month dummies; or ETS. Shrink coefficients toward the parent expenditure-class fit (hierarchical partial pooling) — individual strata are noisy, classes are stable.
- **Moderate vol with seasonality** (apparel strata, household furnishings, recreation goods): SARIMA or seasonal AR with **class-mean-imputation calendar features** (apparel season transitions, markdown months) and hedonic-era drift terms.
- **Bimonthly-collected strata** (flagged `collection: bimonthly` in registry): model the 2-month relative and split, or include odd/even-month staleness dummies — their published monthly m/m alternates between "new information" and "imputed" months.

### Tier 4 — Small/erratic long tail (~5% of weight, ~100+ strata)
Weight < 0.1 and/or noise-dominated (low persistence, no seasonal signal): **inherit the parent expenditure class forecast** (forecast the class with Tier 3, allocate to children by their weight share). Their idiosyncratic error contributes almost nothing to headline; do not burn complexity here.

---

## 3. Aggregation, reconciliation, and outputs

1. **Bottom-up base case:** stratum NSA m/m → weight-aggregate to expenditure classes, major groups, special aggregates (core, energy, services less energy services…), headline. Verify internal consistency: aggregating strata must reproduce the class forecast within tolerance (Tier 4 makes this exact by construction).
2. **SA layer:** apply published seasonal factors per §1; produce SA m/m at stratum/group/headline; reproduce BLS's indirect aggregation structure for SA aggregates.
3. **y/y:** mechanical from the m/m forecast + known history; publish a base-effects table (what y/y does under 0.0/0.2/0.3 m/m scenarios for the next 6 months).
4. **Uncertainty:** per-stratum walk-forward error distributions; headline interval via simulation preserving the historical cross-component error correlation matrix (energy errors correlate; shelter errors are near-independent of energy). Report P10/P50/P90 for headline and core m/m, and the implied y/y distribution.
5. **Attribution:** every forecast ships with a contribution table (component, weight, m/m forecast, pp contribution) and, after each release, an error-attribution table (which components missed, by how many pp of headline).

---

## 4. Auto-triage decision rule (for the ~200 unnamed strata)

Compute per stratum on ≥15 years of NSA m/m: weight `w` (latest RI), volatility `σ` (std of m/m), persistence `ρ` (AR(1)), seasonal strength `s` (R² of month dummies), and registry flags (`alt_data`, `collection`, `formula`).

```
if registry.alt_data or external input mapped        → Tier 1
elif registry.formula in {6MR} or mechanics known    → Tier 2
elif w < 0.1 or (ρ low and s low)                    → Tier 4 (inherit parent)
else                                                 → Tier 3; model = seasonal AR if ρ high,
                                                       SARIMA if s high, ETS otherwise;
                                                       always partial-pooled toward parent class
```
Persist assignments in the registry (`tier`, `model_type`, `input_series[]`, `pass_through_lags`, `event_calendar`) so the triage is auditable and overridable per component.

---

## 5. External input catalog (Tier 1/2 feeds)

| Feed | Access | Components | Cadence |
|---|---|---|---|
| EIA gasoline/diesel/heating oil retail | free API | SETB01, SEHE01 | weekly (Mon) |
| AAA daily gas | free scrape | SETB01 | daily |
| RBOB/Henry Hub/crude futures | free (settle) | energy | daily |
| Manheim UVVI | free headline | SETA02 | mid-month + monthly |
| Black Book | licensed | SETA02 | weekly |
| J.D. Power PIN / Cox ATP & incentives | licensed / partial free | SETA01 | monthly |
| Zillow ZORI, Apartment List | free download | SEHA, SEHC | monthly |
| BLS–Cleveland Fed New Tenant Rent Index | free | SEHA/SEHC lead | quarterly |
| USDA retail food, CME ag futures | free | SAF11 strata | weekly/daily |
| ARC airfares | licensed (else jet fuel + scrape) | SETG01 | monthly |
| Rate-filing trackers | licensed (else AR fallback) | SETE | ongoing |
| CPI seasonal factors + seasonal-aggregation XLSX | free (bls.gov) | SA layer | annual (Feb) |

Every licensed feed must have a documented free fallback; the pipeline runs end-to-end on free data with degraded (reported) accuracy.

## 6. Backtesting protocol — maximum history, three windows (acceptance gate)

Walk-forward throughout (train through t−1, forecast t, roll monthly). NSA CPI is unrevised, so real-time target = final target; input feeds must be lagged to their real-time availability (only EIA weeks published before month-end, Manheim mid-month print, etc.).

**How far back we can honestly go.** The binding constraints are (a) the current CPI item structure dates to the **January 1998 revision** and the geometric-mean formula to **January 1999** — stratum histories before that are a different index; (b) external feeds have staggered inceptions (EIA weekly gasoline ~1993, Manheim ~1995, Apartment List ~2017, ZORI ~2015, New Tenant Rent Index research series back to ~2005); (c) BLS's own method changes mid-sample (alt-data gasoline Jun-2021, J.D. Power new vehicles Apr-2022, annual weights Jan-2023, wireless Jul-2025). So run three nested windows rather than one:

| Window | Span | What's evaluated | Purpose |
|---|---|---|---|
| **A — Long-run statistical** | **~Jan 2000 → present (300+ months)** | Tier 3/4 trend models on every stratum with history, aggregation identity, seasonal layer, plus gasoline Tier 1 (EIA history supports it) | Efficacy across full regimes: dot-com, GFC, 2010s low-flation, COVID, 2021–23 inflation, current episode. This answers "does trend analysis on survey components actually work, and when does it break?" |
| **B — Full system** | **~Jan 2016 → present (~125 months)** | All four tiers with real external feeds (rent indexes exist, Manheim mature) | Efficacy of the complete architecture as it would run today |
| **C — Modern regime** | **Jan 2022 → present** | Same as B | Decision-grade window: current BLS methodology (alt-data gasoline/vehicles, annual weights). Headline claims about live accuracy come from C only |

**Regime handling:** era-specific pass-through coefficients or break dummies at each BLS method change (don't fit one gasoline β across the 2021 source switch); strata born after 1998 enter when available; use **archived relative-importance files** (BLS archives back to 1987) so each backtest month aggregates with the weight vintage that was actually in force — never today's weights retro-applied. Document every break in MODEL_CARD.md.

**Benchmarks every window must report against:** (a) seasonal random walk (m/m = same month last year), (b) AR(1) on headline, (c) component random walk aggregated. The model must beat all three on headline **and** core m/m MAE in windows B and C, and beat (a) and (b) in window A.

**Scores:** headline/core m/m MAE & RMSE (NSA and SA), hit rate on m/m rounded to 0.1, y/y MAE, per-component MAE vs. its own benchmark, interval calibration (P10–P90 coverage ≈ 80%), rolling 24-month MAE plots to expose regime decay, and per-window error attribution by component. Diagnostics on known hard months: January (weight pivot + factor update), Sept–Nov (vehicle changeover), health-insurance reset months, and the COVID collection-disruption months in window A (Mar 2020–mid 2021 — report with and without).

## 7. Known traps (encode, don't discover)

Weight-vintage pivot every January; seasonal factors swap every February (5-yr SA history revision — refit SA-dependent features); bimonthly staleness alternation; shelter turns 3–6 quarters after market rents; gasoline uses full-month averages (a late-month price spike hits both t and t+1); class-mean imputation makes vehicle/apparel CPI move on replacement composition; C-CPI-U revises but CPI-U/W never does; Feb 2025 discontinued some sub-national series — national strata unaffected.