# Heatmap June Projection N/A Audit

Generated before fixes.

## Summary

- Forecast month: 2026-06.
- Heatmap rows inspected: top 80 dashboard rows by current relative importance.
- Before-fix empty June projection cells: 63 of 80.
- Root cause: the heatmap rendered dashboard/cache entries and looked up projections by exact `itemCode` in `latest-forecast.json.components`. The production forecast iterates a smaller non-overlapping forecast universe. Any displayed aggregate, overlapping special aggregate, or excluded child whose exact code was not in that universe rendered `n/a`, even when its children or parent had valid projections.
- This is a pipeline/display mapping gap, not primarily a BLS publication gap or feed outage.

## Priority Findings

1. High-weight components were skipped in the projection column because they were not exact forecast rows:
   - `SEHC01` Owners' equivalent rent of primary residence: excluded because `SEHC` Owners' equivalent rent of residences was the selected forecast unit. `SEHC01` is the only child of `SEHC` but covers about 96% of parent RI, below the forecast-universe descent threshold.
   - `SAF11` Food at home: excluded as a parent; 53 child food-at-home rows have projections.
   - `SEFV` Food away from home: excluded as a parent; 5 child food-away-from-home rows have projections.
   - `SAR` Recreation: excluded as a parent; 15 child recreation rows have projections.
   - `SAA` Apparel: excluded as a parent; 16 child apparel rows have projections.
2. Lower-weight rows could show projections because their exact item codes were selected as forecast units, while larger aggregate parents did not. This made the table look as if the model skipped important components.
3. OER duplicated because both `SEHC` and `SEHC01` are valid dashboard/cache rows. The forecast universe selected `SEHC` only, so `SEHC` got a projection and `SEHC01` did not. For the heatmap projection view, `SEHC` should be kept and `SEHC01` suppressed to avoid a parent/child pair where only one belongs to the non-overlapping forecast partition.
4. No evidence in this audit indicates that the named missing rows failed because Tier 1/Tier 2 feeds errored. The missing rows were absent from `forecast.components`.

## Empty Projection Rows Before Fix

| Code | Name | RI | Parent | Formula | Diagnosis |
|---|---|---:|---|---|---|
| SA0 | All items | 100.000 |  | aggregate | Aggregate/special row displayed; no direct forecast row; should derive from child projections. |
| SA0LE | All items less energy | 92.209 | SAG | aggregate | Aggregate/special row displayed; no direct forecast row; should derive from child projections. |
| SA0L5 | All items less medical care | 91.771 | SAG | aggregate | Aggregate/special row displayed; no direct forecast row; should derive from child projections. |
| SA0L1 | All items less food | 86.553 | SAG | aggregate | Aggregate/special row displayed; no direct forecast row; should derive from child projections. |
| SA0L1E | All items less food and energy | 78.762 | SAG | aggregate | Aggregate/special row displayed; no direct forecast row; should derive from child projections. |
| SA0L2 | All items less shelter | 64.851 | SAG | aggregate | Aggregate/special row displayed; no direct forecast row; should derive from child projections. |
| SAS | Services | 63.265 | SAG | aggregate | Aggregate/special row displayed; no direct forecast row; should derive from child projections. |
| SASLE | Services less energy services | 60.025 | SAG | aggregate | Aggregate/special row displayed; no direct forecast row; should derive from child projections. |
| SASL5 | Services less medical care services | 56.443 | SAG | aggregate | Aggregate/special row displayed; no direct forecast row; should derive from child projections. |
| SAH | Housing | 43.896 | SA0 | aggregate | Aggregate parent displayed; no direct forecast row; should derive from child projections. |
| SAC | Commodities | 36.735 | SAG | aggregate | Aggregate/special row displayed; no direct forecast row; should derive from child projections. |
| SAH1 | Shelter | 35.149 | SAH | aggregate | Aggregate parent displayed; no direct forecast row; should derive from child projections. |
| SAS2RS | Rent of shelter | 34.862 | SAG | aggregate | Aggregate/special row displayed; no direct forecast row; should derive from child projections. |
| SASL2RS | Services less rent of shelter | 28.402 | SAG | aggregate | Aggregate/special row displayed; no direct forecast row; should derive from child projections. |
| SAN | Nondurables | 26.278 | SAG | aggregate | Aggregate/special row displayed; no direct forecast row; should derive from child projections. |
| SEHC01 | Owners' equivalent rent of primary residence | 24.742 | SEHC | 6MR | Excluded child; parent `SEHC` is forecast unit. Suppress child in heatmap projection view. |
| SACL1 | Commodities less food | 23.288 | SAG | aggregate | Aggregate/special row displayed; no direct forecast row; should derive from child projections. |
| SACL11 | Commodities less food and beverages | 22.469 | SAG | aggregate | Aggregate/special row displayed; no direct forecast row; should derive from child projections. |
| SACL1E | Commodities less food and energy commodities | 18.738 | SAG | aggregate | Aggregate/special row displayed; no direct forecast row; should derive from child projections. |
| SAT | Transportation | 17.526 | SA0 | aggregate | Aggregate parent displayed; no direct forecast row; should derive from child projections. |
| SAT1 | Private transportation | 15.834 | SAT | aggregate | Aggregate parent displayed; no direct forecast row; should derive from child projections. |
| SAF | Food and beverages | 14.268 | SA0 | aggregate | Aggregate parent displayed; no direct forecast row; should derive from child projections. |
| SAF1 | Food | 13.447 | SAF | aggregate | Aggregate parent displayed; no direct forecast row; should derive from child projections. |
| SANL1 | Nondurables less food | 12.831 | SAG | aggregate | Aggregate/special row displayed; no direct forecast row; should derive from child projections. |
| SANL11 | Nondurables less food and beverages | 12.012 | SAG | aggregate | Aggregate/special row displayed; no direct forecast row; should derive from child projections. |
| SAD | Durables | 10.457 | SAG | aggregate | Aggregate/special row displayed; no direct forecast row; should derive from child projections. |
| SANL13 | Nondurables less food and apparel | 10.375 | SAG | aggregate | Aggregate/special row displayed; no direct forecast row; should derive from child projections. |
| SAS367 | Other services | 9.660 | SAG | aggregate | Aggregate/special row displayed; no direct forecast row; should derive from child projections. |
| SANL113 | Nondurables less food, beverages, and apparel | 9.554 | SAG | aggregate | Aggregate/special row displayed; no direct forecast row; should derive from child projections. |
| SAM | Medical care | 8.229 | SA0 | aggregate | Aggregate parent displayed; no direct forecast row; should derive from child projections. |
| SAF11 | Food at home | 8.187 | SAF1 | GM | Parent row; 53 child rows have projections; should derive from child projections. |
| SAS24 | Utilities and public transportation | 8.107 | SAG | aggregate | Aggregate/special row displayed; no direct forecast row; should derive from child projections. |
| SA0E | Energy | 7.791 | SAG | aggregate | Aggregate/special row displayed; no direct forecast row; should derive from child projections. |
| SETA | New and used motor vehicles | 6.959 | SAT1 | aggregate | Aggregate parent displayed; no direct forecast row; should derive from child projections. |
| SAN1D | Domestically produced farm food | 6.823 | SAG | aggregate | Aggregate/special row displayed; no direct forecast row; should derive from child projections where available. |
| SAM2 | Medical care services | 6.821 | SAM | aggregate | Aggregate parent displayed; no direct forecast row; should derive from child projections. |
| SAS4 | Transportation services | 6.378 | SAG | aggregate | Aggregate/special row displayed; no direct forecast row; should derive from child projections. |
| SAE | Education and communication | 5.701 | SA0 | aggregate | Aggregate parent displayed; no direct forecast row; should derive from child projections. |
| SEFV | Food away from home | 5.260 | SAF1 | GM | Parent row; 5 child rows have projections; should derive from child projections. |
| SAR | Recreation | 5.031 | SA0 | GM | Parent row; 15 child rows have projections; should derive from child projections. |
| SACE | Energy commodities | 4.550 | SAG | aggregate | Aggregate/special row displayed; no direct forecast row; should derive from child projections. |
| SAH2 | Fuels and utilities | 4.546 | SAH | aggregate | Aggregate parent displayed; no direct forecast row; should derive from child projections. |
| SETB | Motor fuel | 4.378 | SAT1 | aggregate | Aggregate parent displayed; no direct forecast row; should derive from child projections. |
| SAH21 | Household energy | 3.413 | SAH2 | aggregate | Aggregate parent displayed; no direct forecast row; should derive from child projections. |
| SEHF | Energy services | 3.240 | SAH21 | aggregate | Aggregate parent displayed; no direct forecast row; should derive from child projections. |
| SAE21 | Information and information processing | 3.111 | SAE2 | aggregate | Aggregate parent displayed; no direct forecast row; should derive from child projections. |
| SAE1 | Education | 2.524 | SAE | aggregate | Aggregate parent displayed; no direct forecast row; should derive from child projections. |
| SAA | Apparel | 2.458 | SA0 | GM | Parent row; 16 child rows have projections; should derive from child projections. |
| SAG1 | Personal care | 2.444 | SAG | GM | Parent row; children should be used where available. |
| SAF115 | Other food at home | 2.217 | SAF11 | GM | Parent food row; child rows should be used where available. |
| SEMD01 | Hospital services | 2.145 | SEMD | ML elements | Parent/service row not selected as exact forecast unit; should derive or fallback. |
| SAF112 | Meats, poultry, fish, and eggs | 1.943 | SAF11 | GM | Parent food row; child rows should be used where available. |
| SA311 | Apparel less footwear | 1.866 | SAG | aggregate | Aggregate/special row displayed; no direct forecast row; should derive from child projections. |
| SAF1121 | Meats, poultry, and fish | 1.830 | SAF112 | aggregate | Aggregate food row; should derive from child projections. |
| SETG | Public transportation | 1.693 | SAT | aggregate | Aggregate parent displayed; no direct forecast row; should derive from child projections. |
| SEFT | Other foods | 1.676 | SAF115 | aggregate | Aggregate food row; should derive from child projections. |
| SEEE | Information technology, hardware and services | 1.659 | SAE2 | aggregate | Aggregate parent displayed; no direct forecast row; should derive from child projections. |
| SEMC01 | Physicians' services | 1.658 | SEMC | GM/ML elements | Parent/service row not selected as exact forecast unit; should derive or fallback. |
| SEED | Telephone services | 1.451 | SAE21 | aggregate | Aggregate parent displayed; no direct forecast row; should derive from child projections. |
| SAM1 | Medical care commodities | 1.409 | SAM | GM | Parent row; children should be used where available. |
| SEED03 | Wireless telephone services | 1.328 | SEED | GM | Exact code not selected in current forecast universe; should receive fallback projection if displayed. |
| SEEB01 | College tuition and fees | 1.308 | SEEB | GM | Exact code not selected in current forecast universe; should receive fallback projection if displayed. |
| SAF113 | Fruits and vegetables | 1.287 | SAF11 | GM | Parent food row; child rows should be used where available. |

## Planned Fix

- Emit explicit projection rows with non-null `forecast_sa_mm`, `forecast_nsa_mm`, and a fallback-level tag.
- Direct forecast rows use their model output.
- Displayed aggregate rows derive projections from weighted child projections.
- Displayed leaves missing a direct model output use a fallback chain: model attempt if applicable, Tier 3 seasonal AR fallback, then parent-inherit if needed.
- Dashboard heatmap reads projection rows and renders a small badge for the source level.
- Suppress `SEHC01` from the heatmap projection view while retaining `SEHC`, resolving the OER parent/child duplicate.

## After-Fix Counts

- Heatmap rows inspected after suppressing the duplicate OER child: 80.
- After-fix empty June projection cells: 0 of 80.
- OER display resolution: `SEHC` Owners' equivalent rent of residences remains in the heatmap projection view; `SEHC01` Owners' equivalent rent of primary residence is suppressed there to avoid a parent/child duplicate from the non-overlapping forecast partition.
- Projection artifact rows emitted: 400.
- Projection source tags:
  - `model`: 34
  - `aggregate`: 77
  - `AR fallback`: 256
  - `parent`: 33
- The previously missing named rows are now populated as follows:
  - OER: `SEHC` kept with model projection; `SEHC01` suppressed from heatmap projection display.
  - Food at home: derived from child projections.
  - Food away from home: derived from child projections.
  - Recreation: derived from child projections.
  - Apparel: derived from child projections.
