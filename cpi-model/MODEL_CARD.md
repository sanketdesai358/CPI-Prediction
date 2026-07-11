# CPI Model Card

## Lodging away from home: CoStar/STR ADR primary

The production lodging model uses public CoStar/STR U.S. hotel press releases as its primary driver. The source page is `https://www.costar.com/products/str-benchmark/resources/press-releases`. The local public cache currently parses 130 weekly and 31 official monthly U.S. releases, with publication dates from 2022-03-31 through 2026-07-09 and official monthly ADR levels from 2023-10 through 2026-05. The archive advertises older filter years, but older unique releases are not claimed where yearless weekly URL slugs collide or pages are no longer discoverable.

Weekly parsing uses labeled national values (`Occupancy`, `Average daily rate (ADR)`, and `Revenue per available room (RevPAR)`) rather than positional markup. Raw browser-rendered HTML and text are cached under `data/feeds/costar_adr/raw/`. Direct scripted refreshes currently receive HTTP 403 and are reported in feed health; a usable cache is labeled `live_cached`, while an unavailable target-month series is a visible outage that invokes the Tier 3 Seasonal AR fallback.

Weeks crossing month boundaries are allocated one day at a time. For example, 28 June through 4 July contributes three ADR days to June and four to July. Official monthly ADR is retained for history and training after its publication date. The current unpublished month uses the weekly-derived day-weighted level, with the latest published weekly ADR carried forward only for unobserved days. Across 29 months with both constructions, the mean absolute weekly-derived versus official monthly level gap is 0.64%; this is treated as known nowcast/revision error.

The fitted hotels/motels linkage uses `SEHB02` CPI NSA m/m. The current constrained specification has ADR beta 0.013, ADR lag weights 60% at lag 0 and 40% at lag 1, CPI persistence 0.514, and in-sample R-squared 0.315 over 25 complete observations. Occupancy is excluded because its expanding-window MAE does not clear the improvement threshold. From October 2023 through May 2026, official ADR rose 4.3% while the CPI hotels/motels index rose 15.4%, an 11.1 percentage-point level divergence. This is consistent with the caveat that ADR is a changing, mix-weighted average of realized room revenue while CPI prices a more fixed room specification.

The honest common-span Window C comparison currently contains only 13 forecast months: CoStar ADR-primary MAE 2.11% and RMSE 2.52%, versus old hotels/motels Seasonal AR MAE 1.70% and RMSE 2.38%. ADR is adopted as requested despite the weaker short public backtest. For June 2026, five published weekly prints produce a day-weighted ADR of $173.89, +3.19% versus May's official $168.51. The fitted lodging forecast is +2.03% NSA m/m versus +2.61% from the old production `SEHB` Seasonal AR fallback (the narrower `SEHB02` benchmark was +3.00%), reducing the modeled headline contribution by roughly 0.009 percentage point. June is unscored until the 14 July 2026 CPI release.

## Scope

This model forecasts the next unpublished CPI-U reference month from component-level NSA m/m forecasts, then aggregates headline/core from component contributions. It does not forecast headline directly.

## Current Implementation

- Forecast contributions now use a non-overlapping forecast universe with BLS current relative-importance weights. The June 2026 run includes 128 forecast rows with RI coverage of 99.895%; the food branch now descends to RI-bearing leaf strata.
- Tier 1 measurement models use configured external-feed hooks and free fallbacks. Gasoline, fuel oil, vehicles, airfares, and food commodity strata are identified explicitly. Used vehicles now uses the Manheim UVVI SA lag kernel described below rather than the generic Tier 1 fallback.
- Feed health is emitted per run. In the local June 2026 run, EIA gasoline/diesel/heating oil/jet fuel/Henry Hub/electricity, FRED, AAA, Zillow ZORI, Apartment List, BLS R-CPI-NTR, Manheim, BLS food average-price validators, and the USDA food PDFs below load as live feeds. Food futures remain fallback because the tested free CSV endpoints were blocked/rate-limited from this environment.
- Food feeds currently wired live from public sources: USDA boxed beef cutout PM PDF, USDA pork cutout PM PDF, USDA weekly combined shell egg PDF, USDA weekly national chicken PDF, USDA National Dairy Products Sales Report PDF, USDA advanced Class I milk price PDF, and BLS AP retail validators for eggs, milk, bread, ground beef, bacon, chicken, bananas, tomatoes, potatoes, and coffee.
- CME futures feed layer is now defined for the exact 15 products in `CME_FUTURES_LAG_SPEC.md`: ZC, ZW, KE, ZS, ZL, ZM, ZR, LE, GF, HE, DC, CSC, CB, GNF, and DY. The public endpoint pattern implemented is CME `CmeWS` settlements/quotes (`/CmeWS/mvc/Settlements/Futures/Settlements/{product_id}/FUT?...` and `/CmeWS/mvc/Quotes/Future/{product_id}/G?...`) with per-product Stooq fallback. In this environment CME reset/timed out and Stooq was JavaScript-gated, so all futures features are reported as blocked/dropped rather than fabricated.
- Tier 2 structural models encode known BLS mechanics as model classes: shelter distributed lags, retained-earnings health insurance steps, tuition event months, and filing/fee calendar models.
- Tier 3 survey-based components use seasonal AR / SARIMA / ETS-style fallbacks with parent-pooling metadata.
- Tier 4 small or noisy components inherit class trend/seasonality.

## Verified BLS Method Notes

- BLS's medical-care factsheet identifies health insurance as an indirect retained-earnings approach, using retained earnings relative to benefits paid out, with source data from NAIC reports for October and April adjustments and an approximate 10-month lag. Source: https://www.bls.gov/cpi/factsheets/medical-care.htm
- BLS's airline-fares factsheet says the index is monthly and seasonally adjusted at the U.S. level, with web-based fixed-trip pricing specifications such as advance reservation and day-of-week controls. Source: https://www.bls.gov/cpi/factsheets/airline-fares.htm
- BLS's motor-fuel factsheet notes that CPI motor fuel corresponds to average prices over a calendar month and timing alignment explains differences with weekly EIA-style data. Source: https://www.bls.gov/cpi/factsheets/motor-fuel.htm

## Real-Time Availability Rules

- EIA weekly gasoline/diesel: available on the EIA publication day after the reference week; treated as unrevised for backtest simulation.
- EIA daily spot series: used only through observations dated on or before the run date.
- EIA retail electricity: monthly series, used with the latest published month.
- AAA gasoline: current-month daily infill only; archived append-only from the first local run date and not used for historical backtests.
- Zillow ZORI and Apartment List: one-month availability lag; ZORI minor back-revisions are documented as a known assumption.
- BLS R-CPI-NTR: quarterly availability lag; BLS notes the research series is revised and publication has been paused after 2025Q3 as of the current workbook.
- Manheim UVVI: public XLSX/manual override; the model treats the month-end final as available on the 7th calendar day of the following month, rolled forward off weekends. Month `t` Manheim is allowed as the lag-0 input only when that publication date is before the CPI month-`t` release date; otherwise it is omitted rather than backfilled.
- USDA boxed beef and pork cutout PDFs: parsed from official AMS daily PDFs on the report date. The authenticated MARS endpoint exposes the report browser IDs, but the legacy LMR report JSON endpoints returned unavailable/404 from this environment, so the official PDF is the current free live path.
- USDA weekly shell eggs and chicken PDFs: parsed from official AMS weekly PDFs. MARS JSON for these report IDs returned report headers only in this environment.
- USDA dairy PDFs: NDPSR weekly product prices are available Wednesdays with minor revisions; advanced Class I prices are monthly and used for the fluid milk calendar input.
- BLS AP food validators: monthly public AP series, latest published month only, used as retail validation anchors rather than same-day nowcast inputs.
- APHIS HPAI detections: public page is reachable, but the layer/broiler detail sits inside a Tableau dashboard; parsing the workbook data is still required before using 30/60/90-day bird-affected shock variables.
- USDA terminal-market produce: MARS report list is reachable, but the CPI produce basket needs canonical city/item/spec filters before ingesting terminal-market PDFs. This is intentionally marked parser work rather than treated as live.
- CME futures roll rule: continuous futures should use actual listed contracts, roll 10 business days before expiry or the day before first notice day when known, and ratio back-adjust at rolls so roll gaps contribute zero return. The current code includes this machinery and tests, but no production CME continuous history is emitted until live or cached CME settlement payloads exist.

## Known Failure Modes

- January weight-vintage pivots can move contributions even when component forecasts are accurate.
- February seasonal-factor refreshes can alter the SA layer; this build derives deterministic SA offsets from published SA/NSA history until the seasonal-factor XLSX ingestion is wired.
- A live current gasoline quote is not a calendar-month CPI gasoline estimate. Gasoline is now driven by EIA weekly calendar-month averages; AAA is only current-month infill/archive.
- Shelter turns with a long lag; kernels should put most mass on trailing 6-18 months, not current-month rent data.
- Shelter forecast blend: rent and OER use 75% lagged BLS shelter history plus 25% lagged external market-rent overlay. The overlay averages Zillow ZORI, Apartment List national rent history, and BLS/Cleveland Fed New Tenant Rent Index changes over the same broad 6-18 month lag window, with caps to prevent volatile asking-rent data from overwhelming CPI shelter persistence.
- Used vehicles (`SETA02`) is estimated against BLS SA used cars and trucks (`CUSR0000SETA02`) because Manheim UVVI is already seasonally, mix, and mileage adjusted. The live forecast uses the parsimonious Manheim distributed lag requested for production: lag 0 and lag 2 only, with fitted betas loaded from `analysis/used_vehicles/lag_weights.json` (`beta0` about 0.13, `beta2` about 0.21) plus CPI own-persistence (`rho` about 0.47). The selected Manheim pass-through is checked to stay near 0.40 cumulative, not 1:1. Lags 1, 3, and 4 are deliberately excluded because the analysis found them near zero; a richer 0-4 kernel lost in window C.
- Used-vehicle regime guard: the model computes the cumulative retail-vs-wholesale level gap by rebasing CPI SETA02 SA and Manheim UVVI to the same anchor. A stretched gap contributes a small capped mean-reversion adjustment, while low recent SETA02 volatility down-weights the Manheim signal toward the CPI persistence term. This keeps the wholesale signal strongest in high-volatility regimes and quieter in calm markets where the pass-through link is looser.
- Used-vehicle asymmetry: no up/down Manheim split is included because the saved analysis did not confirm a statistically useful asymmetry. A lone two-month lag was rejected for production because it discards the legitimate current-month Manheim final timing edge; the model keeps lag 0 plus lag 2 to capture both the final pre-CPI wholesale signal and the historically important two-month lead.
- Food futures can fail if unauthenticated CSV providers rate-limit or require JavaScript verification.
- Free coffee/grain/livestock futures remain the hardest non-licensed feed because exchange data is delayed/permissioned and free mirrors often rate-limit, block scripted CSV pulls, or change symbols.
- Futures lag profiles: no ridge lag profile is accepted yet because the CME endpoint and Stooq fallback were blocked. The generated `food_futures_backtest` table therefore drops futures for each component pending live/cached history. Expected sanity profiles remain: beef/pork peaks at lags 2-3, feed-cost features at lags 3-6, dairy at lag 0/forward.
- Vehicle and apparel class-mean imputation can move CPI differently from raw market prices during replacement/changeover months.
- Licensed feeds can materially improve Tier 1, but every licensed feed has a free fallback so the system remains runnable.

## Food Commodity-Complex Factor Models

The food-at-home branch now descends to RI-bearing leaf strata instead of forecasting the broad `SAF` aggregate directly. Parent food strata such as beef, pork, poultry, dairy, fats/oils, and food-at-home are derived by weight aggregation from child forecasts.

Each mapped food sub-stratum has a commodity-complex model card:

- Pork: latent factor is USDA pork cutout carcass. Belly maps to bacon; ham maps to ham; loin maps to pork chops; carcass composite maps to other pork.
- Beef: latent factor is USDA boxed beef Choice cutout. Chuck and round map to ground beef and roasts; loin and rib map to steaks; Choice-Select spread is carried as a quality-mix signal.
- Poultry: whole bird and WOGS map to chicken; boneless breast, leg quarters, and wings form the parts basket. BLS only publishes RI for chicken and other uncooked poultry, while fresh whole chicken and chicken parts resolve as non-RI `SS` rows.
- Dairy: Class I advanced price maps to milk; NDPSR cheddar blocks map to cheese; NDPSR butter maps to butter and margarine; NFDM and dry whey feed ice cream and other dairy cost inputs.
- Eggs: Large midpoint is primary; Extra Large/Medium spread is a shortage-stress signal; the model keeps asymmetric pass-through.

Implementation notes:

- All sub-stratum codes are resolved from the generated `cu.item` registry at build time. The current resolution table is emitted in `forecast.json` as `foodSubstrataResolution`.
- Every USDA cut is stored as a named series in `data/feeds/commodity_complex/cut_series.json`.
- Per sub-stratum, the live cut signal enters a lag-0..3 observation equation with an estimated loading and partial pooling toward the complex factor, mirroring the shelter-state-space philosophy in a lightweight free-data form.
- BLS AP validators are used for AP-to-CPI correlations where an AP series exists: bacon, ground beef, chicken, milk, and eggs. Wholesale-to-AP correlations are reported as `n/a` until the local USDA cut archive has enough monthly history.
- Window-C with/without results are emitted to `runs/2026-06/food_commodity_complex_backtest.json` and shown on `/forecast/backtest`. Only granular mappings that beat the prior composite-only mapping are kept in the live forecast; dropped mappings remain visible on model cards for auditability.

Current Window-C keep/drop result in the June 2026 run:

- Kept: uncooked ground beef, milk, butter and margarine, eggs.
- Dropped: bacon, ham, pork chops, other pork, beef roasts, beef steaks, other beef, chicken, other uncooked poultry, cheese, ice cream, and other dairy.

## Backtest Interpretation

The checked-in backtest files now include an EIA gasoline real-feed backtest metric. Window C gasoline NSA m/m R² is above 0.9 in the current run. Broader decision-grade claims still require archived relative-importance vintages and published BLS seasonal-factor XLSX replication.
