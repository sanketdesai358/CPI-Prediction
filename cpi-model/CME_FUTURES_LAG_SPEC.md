# CME Futures Feed + Distributed-Lag Linkage Spec

**Purpose.** Add a live CME futures feed to the cpi-model pipeline and link it to the CPI
food components through estimated distributed lags. Futures are SECONDARY signals: the
USDA wholesale feeds remain the primary next-month (t+1) drivers; the value of futures
is (a) earlier signal and (b) extending the food forecast horizon to t+2...t+6, producing
a forward food-inflation path. Companion docs: `CPI_MODEL_SPEC.md` (tiers, backtest
windows), `FOOD_COMMODITY_FEEDS.md` (USDA feeds already live).

---

## 1. Data source - CME chart-widget JSON endpoint

CME's public chart widgets expose quote/history data. Example widget URL (corn):
```
https://www.cmegroup.com/apps/cmegroup/widgets/productLibs/esignal-charts.html?type=p&code=ZC&title=Chart+-+Jul+2026+Corn&venue=0&monthYear=N6&year=2026&exchangeCode=XCBT&interval=1
```
**Discovery step (do once, then hardcode the endpoint pattern):** load one widget page,
inspect its network requests, identify the underlying JSON quotes/history endpoint the
chart calls, and build the loader against that endpoint directly - never parse the HTML
chart page. Polite rate limits, on-disk cache, delayed data is fine. If the endpoint is
blocked or changes, fall back per product to stooq CSVs and mark it in feed_health.

## 2. Product list (exhaustive - add nothing else)

From https://www.cmegroup.com/markets/products, only these map to CPI food. There are
**no vegetable futures**; fresh produce stays on the USDA terminal-market feed.

| Code | Product | Exchange | Listing cycle (verify live) | CPI linkage | Expected lag peak |
|---|---|---|---|---|---|
| ZC | Corn | XCBT | H,K,N,U,Z | poultry, eggs feed-cost margin | 3-6 mo |
| ZW | SRW Wheat | XCBT | H,K,N,U,Z | bakery/cereals (Tier 3 lead) | 3-6 mo, small beta |
| KE | HRW Wheat | XCBT | H,K,N,U,Z | bakery/cereals | 3-6 mo |
| ZS | Soybeans | XCBT | F,H,K,N,Q,U,X | fats & oils, feed complex | 3-6 mo |
| ZL | Soybean Oil | XCBT | F,H,K,N,Q,U,V,Z | fats & oils | 3-6 mo |
| ZM | Soybean Meal | XCBT | F,H,K,N,Q,U,V,Z | poultry/eggs feed cost | 3-6 mo |
| ZR | Rough Rice | XCBT | F,H,K,N,U,X | rice stratum | 3-6 mo |
| LE | Live Cattle | XCME | G,J,M,Q,V,Z | beef (secondary behind cutout) | 2-3 mo |
| GF | Feeder Cattle | XCME | F,H,J,K,Q,U,V,X | beef, longer lead | 3-6 mo |
| HE | Lean Hogs | XCME | G,J,K,M,N,Q,V,Z | pork (secondary behind cutout) | 2-3 mo |
| DC | Class III Milk | XCME | monthly | dairy - EXCEPTION, see section 4 | 0 / forward |
| CSC | Cash-settled Cheese | XCME | monthly | cheese | 0 / forward |
| CB | Cash-settled Butter | XCME | monthly | butter/fats | 0 / forward |
| GNF | Nonfat Dry Milk | XCME | monthly | dairy | 0 / forward |
| DY | Dry Whey | XCME | monthly | dairy | 0 / forward |

Verify each listing cycle against the live product page at build time - do not trust
this table blindly. ICE softs (KC coffee, SB sugar) are NOT on CME; they remain on the
existing stooq/World Bank feed. Where this CME feed overlaps erroring stooq symbols,
the CME feed replaces them.

## 3. Continuous front-month series (critical correctness section)

Month codes: F,G,H,J,K,M,N,Q,U,V,X,Z = Jan...Dec (so N6 = Jul-2026, Q6 = Aug-2026).

1. **Front-month selection:** the nearest listed contract per the product's actual cycle
   (contracts do not exist every month).
2. **Roll rule:** switch to the next listed contract **10 business days before expiry,
   or the day before first notice day for physically delivered contracts, whichever is
   earlier**. Record every roll date per product.
3. **Splice:** ratio back-adjust history at each roll so the switch contributes exactly
   zero return. NEVER compute m/m across a naive front-month switch - the roll gap
   (contango/backwardation) is not a price change and, uncorrected, injects several
   fake price moves per year per product.
4. **Monthly signal:** m/m change of the **calendar-month average** of the roll-adjusted
   daily series (mirrors CPI's month-average construction; never month-end vs
   month-end). Also expose front + next two deferred raw settles per product (dairy
   forward models need unadjusted deferred prices).
5. **Integrity tests (mandatory):** (a) no single-day move > 15% in any continuous
   series at any roll date; (b) roll dates per product per year match the listing
   cycle count +/-1; (c) units sane per product (cents/bu, dollars/cwt, cents/lb).
6. **Real-time rule:** daily settles are available same evening / T+1; backtests may
   use a month's settles only through the run date.

## 4. Linkage - distributed lags, not hand-picked points

For every futures-feature -> component pair:

- Enter the product's monthly m/m as a **distributed lag, lags 0-6, with ridge-style
  shrinkage** - estimate the lag profile, don't assume it.
- **Dairy exception:** DC/CSC/CB/GNF/DY enter the dairy Tier 1 model at lag 0 AND as
  forward signals - front and deferred dairy futures are the market's forecast of the
  announced Class prices, which retail follows ~1 month later. This is a lead, not a lag.
- **Asymmetric up/down terms** (rockets-and-feathers) optional per feature for livestock
  and feed-cost inputs, matching the existing eggs treatment; keep only if walk-forward
  error improves.
- **Leakage red flag:** fitted beef/pork profiles should peak around lags 2-3 and
  feed-cost profiles around 3-6. A profile loading heavily on lag 0 for these is a red
  flag - investigate timing alignment before accepting it.
- **Hierarchy:** USDA wholesale series stay the primary t+1 drivers. Futures features
  are additive secondary terms; if adding them worsens a component's walk-forward error
  in window C, drop them for that component (report the decision).
- Report every fitted lag profile (bar chart of lag weights, beta, contribution to R2) in
  MODEL_CARD.md and on the dashboard component model cards.

## 5. Forward view (the payoff)

Because lags are estimated, futures observed today carry information about CPI months
ahead. Produce, per food component and for headline food:
- Implied path for **t+1 ... t+6** NSA m/m (t+1 from the full model; t+2+ from the lag
  structure with USDA inputs carried by their own persistence), with widening intervals
  from walk-forward errors at each horizon.
- New dashboard panel on /forecast: "Food forward path" - per-component fan chart +
  a table of implied contributions to headline by horizon, clearly labeled model output.

## 6. Backtest & acceptance additions

- Window C walk-forward, per food component: model WITH futures features vs WITHOUT.
  Keep futures only where they win; publish the comparison table.
- Horizon evaluation: MAE at t+1 through t+6 for each food component vs a
  persistence benchmark at each horizon.
- feed_health: per-product status, last settle date, last roll date, endpoint vs stooq
  fallback flag. History span per product stated in MODEL_CARD.md (backfill as far as
  the endpoint allows; never fabricate).
