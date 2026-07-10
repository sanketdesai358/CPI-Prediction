# CPI Component Data Spec — Excel Workbook + Vercel Dashboard

**Purpose.** Build the measurement layer for a monthly CPI forecasting model. Two deliverables share one data spec:
1. An Excel workbook cataloging every published CPI component — how it is calculated, its current weight, and its last 3 published monthly readings.
2. A Vercel-deployed dashboard presenting the same data interactively, refreshed on BLS release days.

**Primary source of truth: bls.gov.** All numbers must be pulled programmatically at build/refresh time — never hardcoded from memory. This spec was written as of July 2026: the latest published reference month is **May 2026** (released June 10, 2026; headline +0.5% SA m/m, +4.2% NSA y/y; core +0.2% / +2.9%), and the next release is **June 2026 data on July 14, 2026, 8:30 a.m. ET**. "Last 3 months" always means the latest three *published reference months* (currently Mar/Apr/May 2026) — resolve dynamically, never hardcode.

---

## 1. Authoritative data sources

| # | Source | URL | Use |
|---|--------|-----|-----|
| 1 | BLS Public Data API v2 | `https://api.bls.gov/publicAPI/v2/timeseries/data/` (POST, JSON) | Index levels, NSA + SA, all series |
| 2 | API registration (free key) | `https://data.bls.gov/registrationEngine/` | Key limits: **500 queries/day, 50 series/query, 20 years/query**. Store as env var `BLS_API_KEY` |
| 3 | LABSTAT flat files (CPI-U survey `cu`) | `https://download.bls.gov/pub/time.series/cu/` | `cu.series` (full series catalog), `cu.item` (item codes + names), `cu.area`, `cu.data.0.Current` (full current data — bulk alternative to the API). **Requires a real `User-Agent` header with contact email or BLS returns 403** |
| 4 | CPI news release + tables | `https://www.bls.gov/news.release/cpi.nr0.htm`, Table 1: `.../cpi.t01.htm`, Table 2: `.../cpi.t02.htm` | Monthly relative importance column + 1-mo/12-mo changes; available at 8:30 ET on release day (API can lag up to a day) |
| 5 | News Release Companion File (XLSX) + supplemental files | `https://www.bls.gov/web/cpi.supp.toc.htm` | Machine-readable release tables; seasonal factors XLSX; relative importance XLSX; components-for-seasonal-aggregation XLSX; intervention-analysis series list; CPI-U historical cost weights |
| 6 | Relative importance & weight info | `https://www.bls.gov/cpi/tables/relative-importance/` | Annual December RI (Tables 1–7 XLSX), weight-update comparison pages (e.g., `weight-update-comparison-2026.htm`), cost-weights homepage (`cost-weights.htm`) |
| 7 | Handbook of Methods, CPI chapters | `https://www.bls.gov/opub/hom/cpi/design.htm`, `.../data.htm`, `.../calculation.htm` | Formulas, sample design, estimator definitions |
| 8 | Component factsheets index | `https://www.bls.gov/cpi/factsheets/` | Per-component methodology (gasoline, new/used vehicles, health insurance, airline fares, wireless, rent/OER, etc.) — link each component to its factsheet |
| 9 | Quality adjustment | `https://www.bls.gov/cpi/quality-adjustment/` | Which categories use hedonics / cost-based QA |
| 10 | Seasonal adjustment | `https://www.bls.gov/cpi/seasonal-adjustment/` | X-13ARIMA-SEATS practice, Feb factor updates, 5-yr revisions, item aggregation |
| 11 | Release calendar | `https://www.bls.gov/schedule/news_release/cpi.htm` | Drive refresh scheduling and "next release" countdown |
| 12 | Per-series permalink | `https://data.bls.gov/timeseries/{SERIES_ID}` | The link target for every series in both deliverables |

Optional convenience mirror: FRED (`https://fred.stlouisfed.org/series/CPIAUCSL` etc.) — use only as fallback; BLS is authoritative.

---

## 2. CPI structure and series-ID grammar

**Hierarchy.** All items → 8 major groups → expenditure classes → **243 item strata** (the atomic published level). Geographically, 75 PSUs collapse to 32 index areas → 7,776 basic item-area indexes. Special aggregates cut across the tree (core = all items less food & energy; energy; commodities; services; etc.).

**Series-ID grammar (CPI-U, monthly, U.S. city average):**

```
CU  S/U  R  0000  {ITEM_CODE}
│    │   │   │      └ item code (e.g., SA0, SETB01)
│    │   │   └ area code 0000 = U.S. city average
│    │   └ periodicity: R = monthly (S = semiannual)
│    └ seasonal: S = seasonally adjusted, U = unadjusted
└ survey: CU = CPI-U (CW = CPI-W, SU = C-CPI-U)
```

Examples: `CUSR0000SA0` (all items, SA), `CUUR0000SA0` (all items, NSA), `CUSR0000SETA02` (used cars & trucks, SA).

**Validation rule (mandatory).** At build time, download `cu.item` and `cu.series` from LABSTAT and validate every series ID and item name in the component registry against them. Fail the build on any mismatch. Item codes in §3 are believed correct but MUST be machine-verified — do not trust this document over `cu.series`.

---

## 3. Component registry (the core deliverable)

Ship this as `registry.json` in both repos — one entry per component with: `name`, `item_code`, `series_nsa`, `series_sa`, `parent`, `level`, `formula`, `collection`, `qa_method`, `alt_data`, `links[]`, `notes`. The tables below define the contents. Both deliverables should cover **at minimum** the ~45 components below; extend to all 243 strata where the pipeline can enumerate them from `cu.item` (strata are the codes BLS flags at the item-stratum level; include a `display_level` from `cu.item`).

### 3a. Calculation method by layer (applies to every component)

| Layer | Method | Formula (operational) | Forecasting consequence |
|---|---|---|---|
| Lower level, most strata | Weighted **geometric mean** of quote relatives | R = ∏(P_t/P_{t−1})^(w_j/Σw) | Captures within-cell substitution; ~0.2–0.3 pp/yr lower than Laspeyres equivalent |
| Lower level, exception strata | **Modified Laspeyres** | R = Σ(W/P_POPS)·P_t / Σ(W/P_POPS)·P_{t−1} | Exceptions: selected shelter services, selected utilities & government fees, selected medical care services — behave like fixed-quantity indexes |
| Shelter (rent, OER) | **Six-month chained relative**, six rotating panels, monthly link = 6th root | REL_{t−1,t} = (REL_{t−6,t})^(1/6), with age-bias (depreciation) adjustment applied to every rent relative | Mechanically smoothed & lagged ~6+ months vs. spot market rents |
| Upper level, CPI-U/CPI-W | **Lowe fixed-weight** aggregation of the 7,776 basic indexes | CE spending weights, updated each January; 2026 vintage = **2024 CE data** (~24-month average lag) | January weight-pivot regime changes; use weight-vintage dummies |
| Upper level, C-CPI-U | Monthly chained **Törnqvist** | Current + prior month expenditure shares | Revised quarterly, final after 10–12 months |
| Seasonal adjustment | X-13ARIMA-SEATS; factors updated each **February**, prior **5 years revised**; intervention analysis on 57 series for 2026; 36 of 81 aggregation components NSA in 2026 | — | Model NSA first, apply the SA layer separately |

### 3b. Component map — item codes, methods, alternative data

Legend: **GM** = geometric mean; **ML** = modified Laspeyres; **6MR** = six-month chained rent relative. Collection: monthly in all areas unless noted; many non-food/energy C&S items are **bimonthly outside NY/LA/Chicago**. Every row links to `https://data.bls.gov/timeseries/CUUR0000{code}` and `.../CUSR0000{code}` plus its factsheet where one exists.

| Component | Item code | Formula | Data source / collection | Quality adjustment & imputation | Key links (bls.gov) |
|---|---|---|---|---|---|
| All items | SA0 | aggregate | — | — | /cpi/ |
| All items less food & energy (core) | SA0L1E | aggregate | — | — | /cpi/ |
| Food | SAF1 | aggregate | — | — | factsheets |
| Food at home | SAF11 | GM | Direct collection; **monthly in all areas** | Cell-relative imputation common; seasonal-item pricing rules | factsheets/average-food-prices |
| — Cereals & bakery | SAF111 | GM | monthly | cell-relative | — |
| — Meats, poultry, fish, eggs | SAF112 | GM | monthly | cell-relative | — |
| — Dairy & related | SEFJ | GM | monthly | cell-relative | — |
| — Fruits & vegetables | SAF113 | GM | monthly | cell-relative | — |
| — Nonalcoholic beverages | SAF114 | GM | monthly | cell-relative | — |
| — Other food at home | SAF115 | GM | monthly | cell-relative | — |
| Food away from home | SEFV | GM | monthly | slow wage/input pass-through | — |
| Alcoholic beverages | SAF116 | GM | mixed | — | — |
| Energy | SA0E | aggregate | — | — | — |
| — Gasoline (all types) | SETB01 | GM | **Alternative data: secondary-source transaction dataset since June 2021 indexes**; full-month coverage | direct comparison | factsheets/gasoline |
| — Fuel oil | SEHE01 | GM | monthly | — | — |
| — Electricity | SEHF01 | **ML** (utilities exception) | monthly | regulated-price carry-forward | factsheets/electricity |
| — Utility (piped) gas service | SEHF02 | **ML** | monthly | — | — |
| Shelter | SAH1 | aggregate | — | — | factsheets/owners-equivalent-rent-and-rent |
| — Rent of primary residence | SEHA | **6MR** | Housing survey: ~6,000 active units, 6 panels, each unit priced 2×/yr, ⅙ replaced annually; rent quotes not tied to pricing periods | **Age-bias (depreciation) adjustment always applied**; donor imputation for missed collections | handbook + 2023 MLR age-bias article |
| — Owners' equivalent rent (OER) | SEHC | **6MR** | Same renter sample, reweighted to owner stock | age-bias | same |
| — Lodging away from home | SEHB | GM | monthly, volatile small sample | — | — |
| Water/sewer/trash | SEHG | **ML** (gov't fees exception) | monthly/bimonthly | carry-forward for regulated | — |
| Household furnishings & operations | SAH3 | GM | bimonthly outside top-3 areas | hedonics on appliances (washers/dryers, ranges, microwaves) | quality-adjustment page |
| Apparel | SAA | GM | bimonthly outside top-3 areas | **Hedonics + class-mean imputation**; seasonal-item on/off-season pricing rules | quality-adjustment page |
| Transportation | SAT | aggregate | — | — | — |
| — New vehicles | SETA01 | GM | **Alternative data: J.D. Power transaction data since April 2022 indexes** | **Cost-based QA**: manufacturer resource costs + retail markup for qualifying model-year changes; class-mean imputation at changeover | factsheets/new-vehicles + quality-adjustment/new-vehicles.pdf |
| — Used cars & trucks | SETA02 | GM | **J.D. Power Valuation Services** data | Depreciation adjustment + inherited new-vehicle QA | factsheets/used-cars-and-trucks |
| — Motor vehicle parts | SETC | GM | bimonthly | — | — |
| — Motor fuel | SETB | see gasoline | — | — | — |
| — MV maintenance & repair | SETD | GM | bimonthly | — | — |
| — MV insurance | SETE | GM | Premium quotes for fixed risk profiles; **large weight, lumpy filings** | carry-forward between filings | factsheets/motor-vehicle-insurance |
| — Airline fares | SETG01 | GM | Verify current source on factsheet (BLS has researched/deployed secondary data here) | directional fare mix rules | factsheets/airline-fares |
| Medical care | SAM | aggregate | — | — | factsheets/medical-care |
| — Medical care commodities | SAM1 | GM | Rx often via secondary/claims-linked sources — verify factsheet | — | — |
| — Physicians' services | SEMC01 | GM/**ML** elements | Claims-based reimbursement pricing; nonresponse-prone | — | factsheets/medical-care |
| — Hospital services | SEMD01 | **ML** elements (medical exception) | monthly | — | — |
| — Health insurance | SEME | **Indirect retained-earnings method** | Annual insurer financial data, incorporated on a lagged cycle (BLS moved to semiannual incorporation of the retained-earnings update in recent years — **verify current cadence on the health-insurance factsheet**) | — | factsheets/health-insurance |
| Recreation | SAR | GM | bimonthly outside top-3 | hedonics on TVs, audio | — |
| Education & communication | SAE | aggregate | — | — | — |
| — College tuition & fees | SEEB01 | GM | annual repricing pattern concentrated in Aug–Sep | — | factsheets/college-tuition |
| — Wireless telephone services | SEED03 | GM | **Alternative data: secondary-source plan-offer + expenditure data since July 2025 indexes** | **Hedonic imputation** | factsheets + 2024–25 MLR alt-data articles |
| — Internet services | SEEE03 | GM | web collection | hedonics | quality-adjustment page |
| — Smartphones | SEEE04 | GM | Directed substitution since 2018 | hedonics | high-tech MLR article |
| Other goods & services | SAG | aggregate | — | — | — |
| — Tobacco & smoking products | SEGA | GM | monthly | — | — |
| — Personal care | SAG1 | GM | bimonthly | — | — |

**Special aggregates to include as first-class rows:** commodities (SAC), services (SAS), durables (SAD), nondurables (SAN), energy services (SEHF), energy commodities (SACE), services less energy services (SASLE), commodities less food & energy commodities (SACL1E), all items less shelter (SA0L2), rent of shelter (SAS2RS — verify code). Enumerate from `cu.item` rather than trusting this list.

### 3c. Quality-change / missing-data methods (metadata field `qa_method`)

| Method | Where used | Effect |
|---|---|---|
| Direct comparison | Replacement essentially identical | none |
| Direct quality adjustment | Size/cost/hedonic value estimable | official index diverges from raw price series |
| Hedonic adjustment | apparel, footwear, TVs, appliances, internet access, phones/smartwatches, cable/satellite; hedonic *imputation* for wireless | attribute-driven |
| Cell-relative imputation | default for missing quotes; most food/services | inherits peer-cell movement |
| Class-mean imputation | vehicles, durables, apparel at model-line turnover | index moves with replacement composition (Sept–Nov new-vehicle changeover) |
| Carry-forward | regulated prices / no better info | stickiness |
| Age-bias adjustment | rent & OER, always applied | constant-quality rent relatives |
| Cost-based (resource cost) | new vehicles (inherited by used) | quality-cost proxies needed to reconcile with transaction data |

---

## 4. Weights layer (both deliverables must implement this exactly)

Three distinct concepts — surface all three:

1. **CE spending weight vintage.** Updated every January since the Jan-2023 indexes; the 2026 index year uses **2024 CE spending** (avg lag ~24 months). Record the vintage as a field (`weight_vintage: 2024`) and expose the BLS weight-update comparison page for each January pivot.
2. **Relative importance (RI).** The weight expressed as % of all items, **price-updated monthly**. Published: (a) annually for December in the RI Tables 1–7 XLSX; (b) monthly in news-release Tables 1–2 / the Companion XLSX. This is the "weight" column the user sees next to every reading.
3. **Cost weights.** Dollar-level expenditure aggregates on the CPI cost-weights page — useful for contribution math across vintages; note BLS's caveat that they are produced outside official production.

**Price-updating RI to any month m (BLS's own method):**
```
RI_{i,m} = 100 × [ RI_{i,Dec} × (I_{i,m}/I_{i,Dec}) ] / [ 100 × (I_{all,m}/I_{all,Dec}) ]
```
**Contribution of component i to the all-items 1-month % change:**
```
contrib_{i,t} ≈ RI_{i,t−1} × ( I_{i,t}/I_{i,t−1} − 1 )        [in percentage points]
```
Use SA indexes for the SA contribution table and NSA for NSA. Cross-check: Σ contributions ≈ headline m/m (tolerance ±0.05 pp; note aggregation/rounding caveats, and that SA aggregates are built from intermediate aggregates, so bottom-up sums differ slightly).

---

## 5. Deliverable 1 — Excel workbook spec

**Repo:** `cpi-excel/` · **Entry point:** `python build_workbook.py` → `cpi_component_workbook.xlsx` · **Stack:** Python 3.11+, `requests`, `pandas`, `openpyxl`. `BLS_API_KEY` from env. Re-runnable any time to refresh.

### Sheets
1. **README** — data-as-of reference month, build timestamp, next release date (scraped from release calendar), refresh instructions, full source list.
2. **Dashboard** — headline & core: last 3 months of SA m/m, NSA y/y, index levels; energy/food/shelter summary; top-10 contributors table for the latest month.
3. **Component_Tree** — full hierarchy from `cu.item` (`display_level` indent), item code, parent, stratum flag.
4. **Methodology** — one row per registry component: formula (GM/ML/6MR), collection frequency & mode, QA/imputation method, alternative-data source + adoption date, **hyperlinks** to the factsheet, handbook section, and both data.bls.gov series pages.
5. **Weights** — December RI (current vintage), price-updated RI for each of the last 3 months (as Excel formulas per §4), CE weight vintage, link to the weight-update comparison page.
6. **Latest_3M** — the money sheet. One row per component × columns for each of the last 3 reference months: NSA index, SA index, SA m/m %, NSA y/y %, RI weight, contribution to headline m/m. m/m, y/y, and contribution columns are **Excel formulas referencing the raw-data sheets**, not Python-computed constants.
7. **Series_Catalog** — every series ID (NSA + SA) with `HYPERLINK()` to `data.bls.gov/timeseries/{id}`.
8. **Data_NSA**, **Data_SA** — wide format: rows = months (≥ 5 years of history for y/y and seasonal work), columns = series.
9. **Sources** — all URLs from §1.

### Engineering requirements
- Batch API calls ≤50 series/request; respect 500/day; cache raw JSON to `data/raw/` so rebuilds don't re-hit BLS.
- Validate registry against `cu.series`/`cu.item` (custom User-Agent for download.bls.gov); fail loudly on mismatch.
- Derived cells are formulas; hardcoded inputs get a cell comment: `Source: BLS <table/page>, <date>, <URL>`.
- Zero formula errors (#REF!/#DIV/0!/#N/A...) — recalculate and assert before shipping. Professional font; blue = inputs, black = formulas, green = intra-workbook links.
- Number formats: indexes 0.000; percents 0.0%; weights 0.000; negatives in parentheses.
- Unit tests: registry validation, RI price-update math reproduces BLS's published worked example, contribution sum ≈ headline.

---

## 6. Deliverable 2 — Vercel dashboard spec

**Repo:** `cpi-dashboard/` · **Stack:** Next.js 14+ (App Router) + TypeScript + Tailwind + Recharts. Deploy target: Vercel.

### Data layer
- Server-only fetching. Route handlers `/api/series`, `/api/weights`, `/api/registry`; `BLS_API_KEY` in Vercel env, never exposed client-side.
- Cache series JSON (Vercel KV, or `unstable_cache`/ISR with tag revalidation). Client never calls bls.gov directly.
- **Refresh:** `vercel.json` cron at 13:35 UTC (≈8:35 a.m. ET) on scheduled release days (drive from a checked-in copy of the release calendar, refreshed monthly) + a daily 14:00 UTC fallback. On refresh: pull latest month for all registry series, recompute derived fields, revalidate tags.
- Ship `registry.json` (from §3) in-repo; it powers navigation, methodology cards, and link-outs.
- Bulk fallback: LABSTAT `cu.data.0.Current` parse (with proper User-Agent) if API quota is hit.

### Pages
1. **Overview `/`** — headline + core cards (SA m/m, NSA y/y, sparkline), last-3-months table mirroring Excel `Latest_3M`, next-release countdown, latest-month contribution waterfall (energy vs. core vs. food).
2. **Explorer `/components`** — treemap sized by current RI weight, colored by latest SA m/m; click to drill down the hierarchy; toggle m/m ↔ y/y, SA ↔ NSA.
3. **Component detail `/components/[itemCode]`** — chart (index level + m/m + y/y, SA/NSA toggle, 1y/5y/max ranges); **methodology card**: lower-level formula, collection frequency/mode, QA & imputation method, alternative-data source and adoption date, weight vintage + current RI, deep links (factsheet, handbook chapter, both data.bls.gov series pages); last-3-months mini-table with weight and contribution.
4. **Heatmap `/heatmap`** — components × last 24 months of SA m/m, diverging color scale, sorted by weight.
5. **Contributions `/contributions`** — waterfall for any selected month; toggle top-level groups ↔ strata; must visibly reconcile to headline (show residual).
6. **Methodology `/methodology`** — rendered version of §3–§4 tables with the forecasting notes from §7.

### Non-functional
- ISR everywhere; page loads must not block on BLS. "Data as of {refMonth}, released {releaseDate}, source: U.S. Bureau of Labor Statistics" footer on every page. Mobile-responsive. Loading/error states for every widget. Type-safe (`SeriesPoint`, `RegistryEntry`, `WeightVintage` types).

---

## 7. Forecast-model hooks (why the metadata matters)

Encode these as flags in `registry.json` so the model layer downstream can consume them:

- **Pricing periods:** most quotes fall in one of three ~10-day windows; an item stays in its assigned period for its ~4-year sample life. Build pricing-period averages of daily predictors (e.g., gasoline), not calendar-month averages.
- **Bimonthly collection** outside NY/LA/Chicago for many non-food/energy items → odd/even-month staleness features (`collection: bimonthly` flag).
- **Shelter:** six-panel, six-month relative with age-bias adjustment → map market-rent indexes (Zillow ZORI, BLS/Cleveland Fed New Tenant Rent Index) through a 6-month smoothing/lag observation equation; never one-for-one.
- **Vehicles:** class-mean imputation + cost-based QA at model-year changeover (Sept–Nov) → changeover dummies; pair Manheim/auction data (used) and transaction/incentive data (new) with quality-cost proxies.
- **Health insurance:** retained-earnings method with lagged annual source data → step-change risk at each incorporation date; verify cadence on the factsheet each fall.
- **Weight regime:** January vintage dummies; RI drifts within year via price-updating (energy RI rises mechanically when energy outpaces headline).
- **Seasonal factors:** revised every February for prior 5 years → forecast NSA components, apply the SA layer separately; track the intervention-analysis series list (57 series in 2026).
- **Revisions:** CPI-U/CPI-W final at release; C-CPI-U revised quarterly for 10–12 months.

### External predictor map (for the model, listed in Methodology page/sheet)
| Component | Market-data predictors |
|---|---|
| Gasoline | EIA weekly retail, OPIS/AAA daily, RBOB futures + crack spreads — aggregated to the three pricing periods |
| Rent/OER | ZORI, Apartment List, BLS-Cleveland Fed New Tenant Rent Index, vacancy, new-lease vs. renewal spreads |
| Used vehicles | Manheim UVVI, Black Book — lead CPI by ~1–2 months |
| New vehicles | J.D. Power PIN retail data, incentives, inventory/days-supply |
| Airfares | ARC ticketing data, jet fuel |
| Food at home | USDA, futures (live cattle, corn, wheat), scanner data |
| Wireless/tech | carrier plan-offer scrapes, launch calendars |

---

## 8. Known ambiguities (do not paper over)

- BLS reports ~6,000 active housing units (technical note) vs. ~8,000 monthly housing quotes (handbook) — related but distinct concepts; present both with their sources.
- ~22,000 retail establishments vs. ~80,000 monthly item quotes — locations vs. quote-level observations.
- A standalone "overlap" QA method is not documented in current BLS web materials — treat as unspecified.
- Item codes marked "verify" in §3b must be resolved against `cu.item` at build time; any component whose current data source can't be confirmed on its factsheet gets `alt_data: "verify — factsheet"` rather than a guess.
