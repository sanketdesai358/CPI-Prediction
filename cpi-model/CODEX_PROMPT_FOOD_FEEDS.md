# CODEX PROMPT — Connect CPI Food Components to Real-Time Public Feeds

You are implementing new real-time food-commodity data feeds for the CPI component
forecasting model in this repository. Follow the existing code conventions exactly. Do
**not** invent series IDs, report slugs, or stratum codes — resolve every identifier LIVE
at build time from the sources named below, and if anything fails to resolve, **fail
loudly and stop with a list of manual steps** rather than guessing or faking data.

Source-of-truth for component mappings and the exact market cut per commodity:
`FOOD_COMMODITY_FEEDS.md` (the food & commodity feed catalog). Read it first. This prompt
pins the endpoints and wiring; the catalog pins which series/cut to extract per component.

---

## 0. Repository facts you must build on (already verified — do not re-derive)

- Package: `cpi-model/cpi_model/`. Feeds live in `cpi_model/feeds.py`.
- Paths (`cpi_model/paths.py`): `ROOT` = `cpi-model/`, `WORKSPACE` = repo root
  (`c-users-sanke-onedrive-documents-cpi/`). `REGISTRY_PATH` = `ROOT/registry.json`,
  `EXTENDED_REGISTRY_PATH` = `ROOT/extended_registry.json`, `RUNS_DIR` = `ROOT/runs`,
  `DATA_DIR` = `ROOT/data`, `FEED_CACHE_DIR` = `ROOT/data/feeds`.
- Env loading: `load_env()` in `feeds.py` reads `WORKSPACE/.env` then `ROOT/.env` with
  `os.environ.setdefault`. **Reference keys via `os.environ` only — never hard-code or
  print key values** (in logs, caches, artifacts, or this prompt's outputs).
- `.env` is gitignored at both repo root and `cpi-model/`. Confirm this still holds before
  writing anything that could contain a secret.
- **Feed record schema (match exactly).** Every fetcher returns a dict shaped like the
  existing `fetch_futures` / `fetch_eia_series` return value:
  ```python
  {
      "feed": <str>,                    # human name, e.g. "MARS Egg Markets Overview"
      "status": <str>,                  # "live" | "partial" | "unavailable" | "fallback"
      "lastObservationDate": <str>,     # ISO date of newest obs
      "latestValue": <float>,
      "unit": <str>,
      "observations": [ {"date": str, "value": float, "label": str}, ... ],
      "points": [ {"date": str, "value": float}, ... ],
      "publishDatetime": <str|None>,    # NEW: source publication timestamp (see §8)
      "error": <str|None>,
  }
  ```
  Use the existing helpers: `_status_error(feed, status, detail, unit)` for failures,
  `_series_points(rows, key)` to build point lists, `_check_gaps(periods, max_gap_days)`
  for staleness, `_fetch_text(url)` / `_get_json(base, params)` for HTTP (they already
  send `USER_AGENT` and route errors through `_redact`).
- Aggregation: `monthly_average(points, month)` computes the calendar-month mean — use it
  for every daily/weekly feed (CPI compares calendar-month means).
- Registration of feeds: add each new fetcher to `collect_feeds()` and wire components in
  the `TIER_FEEDS` map (itemCode → `{name, tier, primary, secondary, unit, env, requires}`).
- Health: `build_feed_health(month, write_snapshots=True)` writes
  `RUNS_DIR/<month>/feed_health.json` via `component_status()`. New food components must
  appear there with `status` = `live` (only stooq-fallback items may show `fallback`).
- **Extend `_redact()`**: it currently redacts only `EIA_API_KEY` and `FRED_API_KEY`. Add
  `MARS_API_KEY` and `BLS_API_KEY` to its redaction list so keys never leak into
  `feed_health.json` error strings or cached snapshots.
- **Extend `USER_AGENT` for BLS**: the current constant
  (`"cpi-component-dashboard/0.2 (+local research; polite cache)"`) has **no contact
  email**. BLS `download.bls.gov` flat files return **403** without a contact email in the
  UA. Send a UA containing a contact email (e.g. `sanketsdesai.1995@gmail.com`) on all
  `download.bls.gov` and `api.bls.gov` requests.

---

## 1. PRECONDITIONS — verify keys before any fetch (fail loudly)

`load_env()` then assert presence in `os.environ`:
- `MARS_API_KEY` — **present** (added to repo-root `.env`; smoke-tested 200 OK).
  MARS uses **HTTP Basic Auth with the key as USERNAME and empty password**:
  `requests.get(url, auth=(os.environ["MARS_API_KEY"], ""))` (or urllib with an
  `Authorization: Basic base64(key + ":")` header). Do a one-GET smoke test to
  `https://marsapi.ams.usda.gov/services/v1.2/reports` and confirm HTTP 200 before
  proceeding.
- `FRED_API_KEY`, `EIA_API_KEY` — present.
- **`BLS_API_KEY` — MISSING from `.env`.** Section 4 ongoing pulls use BLS API v2, which
  needs this key. **Do not fabricate one.** If it is still absent at build time, **stop**
  and emit this manual step:
  > Register for a free BLS API v2 key at https://data.bls.gov/registrationEngine/ and add
  > `BLS_API_KEY=<value>` to the repo-root `.env` (`WORKSPACE/.env`). Do not commit `.env`.

  Note: BLS **flat-file** resolution in §4 (open `download.bls.gov` files) does not require
  a key and can proceed with just a contact-email User-Agent; only the **ongoing v2 API
  pulls** are blocked without `BLS_API_KEY`.

---

## 2. SOURCE 1 — USDA MARS API (Market News)

- Base: `https://marsapi.ams.usda.gov/services/v1.2/reports`
- Report browser (human reference): `https://mymarketnews.ams.usda.gov`
- Auth: Basic, key as username / empty password (see §1).

**Action A — resolve slugs LIVE.** `GET` the full report list, then search
`report_title` (case-insensitive substring) to pin the numeric `slug_id` for each report.
Do not hard-code slugs from memory; resolve at build time and emit a resolution table.
Report titles to resolve (from the catalog):

| Catalog report | Component(s) | Search hint |
|---|---|---|
| Egg Markets Overview | eggs | "Egg Markets Overview" |
| Daily/Weekly Combined Regional Shell Eggs | eggs | "Shell Eggs" + regional/combined |
| Cage-free shell egg report | eggs | "Cage-Free" shell egg |
| National Retail Report — egg feature activity | eggs (retail lead) | "National Retail Report" (shell eggs) |
| National Daily Boxed Beef Cutout — AM | beef & veal | "Boxed Beef Cutout" morning |
| National Daily Boxed Beef Cutout — PM | beef & veal | "Boxed Beef Cutout" afternoon |
| Comprehensive Boxed Beef Cutout | beef & veal | "Comprehensive" boxed beef |
| 5-Area Weekly Direct Slaughter Cattle | beef (upstream) | "5 Area" / "Direct Slaughter Cattle" |
| National Daily Pork Cutout (negotiated, FOB) | pork | "Pork Cutout" negotiated |
| Weekly broiler/chicken composite + parts | poultry | "Broiler" / "Chicken" national weighted |
| National Dairy Products Sales Report (NDPSR) | milk, cheese, dairy | "National Dairy Products Sales" |
| Announced Class milk prices | milk, dairy | "Class" price announcement (Class I mover, III, IV) |
| Terminal Market reports (produce basket) | fresh fruits/veg | per-city "Terminal Market" for the 10 items |

For each resolved report emit: `catalog name → slug_id → slug_name → one sample record`.
Flag any that fail to resolve; do not proceed with a guessed slug.

**Action B — pin field filters from a real response.** For each report, `GET` it, inspect
the JSON, and hard-code the filter per the catalog's exact-cut column. Minimum required
cuts:
- **Eggs (Combined Regional Shell Eggs):** region = *Combined Regional*, class = *White*,
  grade = *Grade A*, size = *Large*, value = **midpoint of the reported price range**
  (¢/dozen). Capture Jumbo/Extra-Large/Medium as secondary size columns. From Egg Markets
  Overview take the national wholesale Large White headline + the cage-free wholesale +
  California-compliant prices.
- **Beef:** **Choice cutout value ($/cwt)** as primary; also Select cutout and the
  Choice–Select spread; rib/loin/chuck/round primals secondary. Use the PM print when
  present (see timing §8).
- **Pork:** **cutout composite ($/cwt)** primary; primal values secondary, **including the
  belly primal** (bacon driver).
- **Dairy (NDPSR):** cheese 40-lb **blocks**, cheese **barrels**, **butter**, **NFDM**,
  dry whey ($/lb). Announced Class prices: **Class I mover**, Class III, Class IV.
- **Poultry:** national composite weighted-average whole-broiler price + parts
  (boneless/skinless breast, wings, leg quarters).
- **Produce basket (Terminal Market):** for each of the 10 canonical specs in the catalog
  (bananas; Gala apples WA extra-fancy cartons; CA navel oranges; round/vine tomatoes
  FL/Mexico; iceberg + romaine CA/AZ; ID russet potatoes; yellow onions; CA strawberries;
  Mexico-crossing avocados; table grapes), extract the **midpoint of the mostly/range
  price** per report city, then aggregate cities by **simple average**.

Specify units, unit conversions (¢/dozen ↔ $/dozen, $/cwt), and null/holiday handling
(carry-forward vs. skip) for each feed.

**Action C — stitch legacy history.** Where a report carries a legacy `LM_XX###` code,
pull its legacy history and stitch it ahead of the current MARS series, targeting **≥10
years per feed** so pass-through βs span regimes. Record the stitch boundary in the
snapshot.

---

## 3. SOURCE 2 — CME settlements (delayed OK)

- Settlement pages: `https://www.cmegroup.com/markets/agriculture.html`
- Symbols to pull, **front month + next two deferred**, daily settles:
  `ZC` corn, `ZW` SRW wheat, `KE` HRW wheat, `ZS` soybeans, `ZL` soybean oil,
  `LE` live cattle, `GF` feeder cattle, `HE` lean hogs, `DC` Class III milk,
  `CSC` cheese, `CB` butter.
- **Extend the existing `fetch_futures()`** — it currently pulls Yahoo Finance daily CSVs
  for only 4 symbols (corn, wheat, live cattle, coffee) and is mislabeled "Stooq". Replace
  it with a CME-settlement-first fetcher covering the full symbol set above.
- **Action:** attempt CME settlement pages first. If the page structure blocks scraping,
  fall back to `https://stooq.com` daily CSVs per symbol
  (`https://stooq.com/q/d/l/?s=<symbol>&i=d`) and record `status = "fallback"` in
  `feed_health.json` for that symbol. Delayed data is acceptable.

---

## 4. SOURCE 3 — ICE softs (coffee, sugar) — no free ICE endpoint

- Coffee **KC** (arabica) and sugar **SB** (#11): pull from `https://stooq.com` CSVs.
- Monthly fallback: **World Bank Pink Sheet** at
  `https://www.worldbank.org/en/research/commodity-markets` (arabica/robusta, sugar).
- Record `status = "fallback"` when the monthly Pink Sheet is used instead of daily stooq.

---

## 5. SOURCE 4 — BLS flat files + API v2

Resolve all identifiers **programmatically at build time** from the flat files; never
hard-code from memory. Send a User-Agent with a contact email (or BLS returns 403).

- **Average Price (AP)** — `https://download.bls.gov/pub/time.series/ap/`
  (`ap.item`, `ap.series`, `ap.data.0.Current`). Resolve AP series IDs for: **eggs
  (Grade A large, dozen), milk (whole, gallon), bread, ground beef (100%, lb), bacon,
  chicken, bananas, tomatoes, potatoes, coffee (100% ground roast, lb)**. These are the
  Tier-1 **validation** series.
- **PPI commodity** — `https://download.bls.gov/pub/time.series/wp/` and **PPI industry**
  — `https://download.bls.gov/pub/time.series/pc/`. Resolve series for: **flour milling,
  commercial bakery, beef/veal, pork, poultry, dairy, beverage manufacturing, snack food,
  paperboard containers, aluminum cans, general freight trucking.**
- **CPI strata** — `https://download.bls.gov/pub/time.series/cu/` (`cu.item`). Pin the
  exact CPI stratum codes for: eggs, beef and veal, pork, poultry, milk, cheese and
  related, fresh fruits, fresh vegetables, coffee, bread/cereals & bakery, snacks/other
  processed, nonalcoholic beverages, fats and oils. Verify against `cu.item` at build
  time (do not trust the SEFH-family guesses in the catalog without confirmation).
- **Ongoing pulls** go through the existing BLS API v2 client:
  `https://api.bls.gov/publicAPI/v2/timeseries/data/` with `BLS_API_KEY` (see §1 — this
  key is currently MISSING; block ongoing pulls and emit the manual step if absent).

Emit a resolution table: `catalog name → resolved ID → sample record`. Flag any miss.

---

## 6. SOURCE 5 — APHIS HPAI detections

- URL: `https://www.aphis.usda.gov/livestock-poultry-disease/avian/avian-influenza/hpai-detections/commercial-backyard-flocks`
- **Action:** download the detections table. Filter **commercial table-egg layer** flocks
  and **broiler** flocks **separately**. Build trailing **30 / 60 / 90-day birds-affected
  sums** per group.
- Wire the **layer** signal as a supply-shock feature into the **eggs** Tier-1 model and
  the **broiler** signal into the **poultry** Tier-1 model — keep them as **separate
  features** (different bird populations, different magnitudes).

---

## 7. NORMALIZATION, CACHING, SANITY

For every source: normalize to the Feed record schema in §0; write a local snapshot into
`FEED_CACHE_DIR/<feed>/…` when `write_snapshots=True`; attach `publishDatetime`; apply
unit sanity checks (min/max bounds per feed, reject nonpositive prices) mirroring the
`min`/`max` pattern in `EIA_SERIES`. Register each fetcher in `collect_feeds()` and each
component in `TIER_FEEDS`. Aggregate every daily/weekly series to calendar-month means via
`monthly_average(points, month)`.

---

## 8. PUBLICATION TIMING (real-time backtest enforcement)

Record each report's publication time and enforce point-in-time availability in backtests
(a month's value is only usable once actually published):
- Boxed beef **PM** ~ late afternoon CT (prefer PM over AM within a day).
- Egg Markets Overview — **Fridays**.
- NDPSR — **Wednesdays**.
- Announced Class prices — administered-price calendar; Class I mover announced in advance
  (treat like the medical fee-schedule calendar inputs).
Populate `publishDatetime` on each record and gate backtest reads on it.

---

## 9. MODEL WIRING

**Tier 1 measurement models** (with catalog pass-through lags):
- **Eggs** — wholesale→CPI ~1 month, **asymmetric** (spikes pass faster than declines);
  encode asymmetric lag terms. HPAI layer signal as supply shock.
- **Beef & veal** — cutout leads CPI **1–2 months**.
- **Pork** — cutout (incl. belly) leads **1–2 months**.
- **Poultry** — parts-weighted; HPAI broiler signal; feed-cost proxy (corn + soybean meal)
  as slow secondary.
- **Dairy** (milk, cheese) — retail follows the **announced Class I mover with ~1-month
  lag**; use the administered-price calendar.
- **Coffee** — green→retail **2–4 months**, margin-buffered; expect low β / long lags —
  do not force-fit.
- **Produce basket** — fixed CPI-weighted basket, canonical spec per item, city simple
  average.

**Tier 3 (processed strata)** — bread, cereals/bakery, snacks, nonalcoholic beverages,
fats/oils: model as trend with **1–3 month PPI leads only**. Do **not** build
multi-commodity regressions (overfit risk). Futures/sugar enter as weak secondary signals
only.

---

## 10. VALIDATION

For **every Tier-1 food model**, before it enters CPI aggregation, compute same-month
correlation against its BLS **AP** retail series (§5) and **report the correlations**.
A Tier-1 model that does not track its AP validator is not trusted — surface it, don't
silently ship it.

---

## 11. ACCEPTANCE CRITERIA

1. All food feeds appear in `RUNS_DIR/<month>/feed_health.json` with `status = "live"`
   (only stooq/Pink-Sheet-fallback items may show `status = "fallback"`).
2. ≥10-year stitched history per feed **where the source allows** (MARS legacy `LM_XX` +
   current slug; BLS full history).
3. Egg and beef Tier-1 backtests **beat their Tier-3 fallback in window C**.
4. AP validation correlations reported for every Tier-1 food model.
5. Real-time publication timing enforced in backtests (§8).
6. `_redact` extended to cover `MARS_API_KEY` + `BLS_API_KEY`; no key value appears in any
   artifact.
7. Resolution tables emitted (MARS slugs, BLS AP/PPI IDs, CPI `cu.item` codes) with any
   unresolved identifier flagged, not guessed.

**Finish by** rerunning the current-month forecast and producing a **food-component diff
report** versus the prior run, flagging any component that moves the headline by more than
**0.02 pp**.

---

## 12. FAIL-LOUD RULES (non-negotiable)

- If any key is missing (currently: **`BLS_API_KEY`**) or any endpoint fails, **stop and
  list the manual steps** — never fake or guess data, series IDs, report slugs, or stratum
  codes.
- Never print or persist key values; reference `os.environ` only; keep `.env` gitignored.
- Prefer point-in-time-correct data over completeness: a feed that cannot be made
  real-time-honest should be marked `unavailable`, not backfilled with look-ahead data.

---

### Build-time status snapshot (as of prompt authoring)
- `MARS_API_KEY`: **present** in repo-root `.env`, Basic-auth smoke test returned **200**.
- `EIA_API_KEY`, `FRED_API_KEY`: present.
- `BLS_API_KEY`: **MISSING** — blocks §5 ongoing API v2 pulls until registered/added.
- Existing `fetch_futures()` pulls Yahoo CSVs (4 symbols, mislabeled "Stooq") — replace per §3.
- `USER_AGENT` lacks a contact email — add one for BLS per §0.
