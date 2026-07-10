# CPI Component-Level Forecast Model

`cpi-model` forecasts the next unpublished CPI-U reference month bottom-up from component forecasts. It consumes the validated `registry.json` from `cpi-excel`, extends it with model tiers, and emits forecast/backtest/score artifacts that the dashboard can ingest.

## Commands

```powershell
python -m cpi_model.triage --refresh
python -m cpi_model.run --month 2026-06
python -m cpi_model.backtest --start 2022-01
python -m cpi_model.score --month 2026-06
```

Outputs:

- `extended_registry.json`
- `triage_report.md`
- `runs/{month}/forecast.json`
- `runs/{month}/forecast.md`
- `runs/{month}/feed_health.json`
- `runs/{month}/inputs/*`
- `runs/{month}/score.json`
- `backtest/{window}/results.json`

## Free vs Licensed Feeds

The pipeline runs end-to-end on free BLS/LABSTAT data and now emits an explicit feed-health report for Tier 1/2 external inputs. `runs/{month}/feed_health.json` is copied to the dashboard so `/forecast` shows live, partial, blocked, and fallback status next to the forecast.

- `EIA_API_KEY` is required before EIA gasoline, diesel, heating oil, jet fuel, Henry Hub, and electricity series can be used.
- `FRED_API_KEY` enables the FRED mirror layer.
- AAA national gasoline is scraped as a live current snapshot and archived append-only under `data/aaa/daily_regular.csv`; EIA weekly gasoline remains the historical record.
- Zillow ZORI, Apartment List, BLS R-CPI-NTR, Manheim UVVI, EIA, FRED, and AAA write local caches under `data/feeds/`.
- Food futures are attempted through an unauthenticated free CSV endpoint. If the provider rate-limits or JS-gates the request, the feed is marked fallback rather than faked.
- Licensed-only gaps such as motor-vehicle insurance rate filings are marked separately.
- When a feed is unavailable, the model records a loud `driverSnapshot` fallback such as recent CPI-timed movement, distributed shelter lag, or event-month drift.

## Dashboard Upload

For the local dashboard, copy:

```powershell
Copy-Item runs\2026-06\forecast.json ..\cpi-dashboard\src\data\forecast\latest-forecast.json -Force
Copy-Item runs\2026-06\feed_health.json ..\cpi-dashboard\src\data\forecast\feed-health.json -Force
Copy-Item runs\2026-06\diff_vs_scaffold.json ..\cpi-dashboard\src\data\forecast\diff-vs-scaffold.json -Force
Copy-Item runs\2026-06\score.json ..\cpi-dashboard\src\data\forecast\latest-score.json -Force
Copy-Item backtest\A\results.json ..\cpi-dashboard\src\data\forecast\backtest-A.json -Force
Copy-Item backtest\B\results.json ..\cpi-dashboard\src\data\forecast\backtest-B.json -Force
Copy-Item backtest\C\results.json ..\cpi-dashboard\src\data\forecast\backtest-C.json -Force
Copy-Item extended_registry.json ..\cpi-dashboard\src\data\extended-registry.json -Force
```

For Vercel, replace the copy step with Blob/KV upload from the same files. The dashboard route handlers are written so a Blob/KV fetch can replace the checked-in JSON convention without touching page code.

## Release Morning Runbook

1. 8:30 ET: BLS publishes CPI.
2. Refresh actuals in `cpi-excel` / dashboard cache.
3. Run `python -m cpi_model.score --month YYYY-MM` for the forecasted reference month.
4. Upload/copy `score.json` to the dashboard forecast data store.
5. `/forecast/track` updates with forecast-vs-actual and error attribution.

## Caveats

This local build is deterministic and deployable, but it is not claiming a decision-grade backtest until archived RI vintages, published seasonal-factor XLSX files, and real-time external-feed snapshots are wired in. The code keeps those requirements visible in configs, `MODEL_CARD.md`, and diagnostics rather than hiding them.
