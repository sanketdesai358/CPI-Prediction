# CPI Dashboard

Next.js App Router dashboard for the CPI-U component registry produced by the companion Excel pipeline.

## Stack

- Next.js 15 App Router
- TypeScript
- Tailwind CSS
- Recharts
- Vercel cron

## Local Setup

```powershell
pnpm install
pnpm build
pnpm dev
```

Optional environment variables:

```powershell
$env:BLS_API_KEY = "your-key"
$env:BLS_USER_AGENT = "Your Name your.email@example.com"
```

Register a free BLS key at https://data.bls.gov/registrationEngine/.

## Data Model

The app ships with:

- `src/data/registry.json`: validated component registry copied verbatim from `cpi-excel`.
- `src/data/dashboard-cache.json`: seeded 72-month CPI cache used for server rendering.
- `src/data/release-calendar.json`: checked-in BLS CPI release calendar.

All direct BLS access is server-side only. The BLS client in `src/lib/bls.ts` batches at 50 series per request when `BLS_API_KEY` is set and 25 when it is not. Client components receive prepared props from server components and never call `bls.gov`.

## Refresh

Refresh the checked-in release calendar:

```powershell
pnpm refresh:calendar
```

Smoke-test BLS API access:

```powershell
pnpm refresh:data
```

Regenerate the seed cache from the companion workbook:

```powershell
pnpm seed:cache
```

`vercel.json` defines two crons:

- `35 13 * * *` calls `/api/refresh?mode=release`; the route refreshes only when `release-calendar.json` marks the current date as a CPI release day.
- `0 14 * * *` calls `/api/refresh?mode=daily`; the route revalidates the CPI data tag daily.

## Forecast Ingestion

The companion `cpi-model` repo writes:

- `runs/{month}/forecast.json`
- `runs/{month}/score.json`
- `backtest/A/results.json`
- `backtest/B/results.json`
- `backtest/C/results.json`
- `extended_registry.json`

For the checked-in/local convention used by this dashboard, copy them to:

```powershell
Copy-Item ..\cpi-model\runs\2026-06\forecast.json src\data\forecast\latest-forecast.json -Force
Copy-Item ..\cpi-model\runs\2026-06\score.json src\data\forecast\latest-score.json -Force
Copy-Item ..\cpi-model\backtest\A\results.json src\data\forecast\backtest-A.json -Force
Copy-Item ..\cpi-model\backtest\B\results.json src\data\forecast\backtest-B.json -Force
Copy-Item ..\cpi-model\backtest\C\results.json src\data\forecast\backtest-C.json -Force
Copy-Item ..\cpi-model\extended_registry.json src\data\extended-registry.json -Force
```

For a private Vercel production app, use the same file payloads with Vercel Blob or KV, then replace the static JSON imports in `src/lib/data.ts` with Blob/KV fetches while preserving the `ForecastRun`, `ScoreResult`, and `BacktestResult` types. `/api/forecast` exposes the currently loaded forecast, score, and backtests.

Release morning:

1. 8:30 ET BLS release posts.
2. Refresh actual CPI data.
3. Run `python -m cpi_model.score --month YYYY-MM`.
4. Upload/copy the resulting `score.json`.
5. `/forecast/track` updates with the scored actual and attribution.

## Pages

- `/`: headline/core cards, last-three-month table, release countdown, contribution waterfall
- `/components`: weight-sized component map and catalog
- `/components/[itemCode]`: time series, methodology, weights, BLS links
- `/heatmap`: last 24 months of SA m/m by component
- `/contributions`: month-selectable contribution waterfall with residual
- `/methodology`: registry methods, weight formulas, and external predictor map
- `/forecast`: next-print forecast with intervals and full component table
- `/forecast/track`: forecast-vs-actual and release attribution
- `/forecast/backtest`: three-window diagnostics

## Deploy

Create a Vercel project from this folder. `vercel.json` uses the public build command:

```powershell
pnpm install
pnpm run build:public
```

`build:public` temporarily swaps `src/data` to a sanitized copy, runs `next build`, and restores the full local data afterward. The deployed bundle keeps the dashboard numbers, CPI history, weights, and public registry context, but hides live-feed diagnostics, model driver snapshots, input series, lag profiles, commodity model details, and scaffold/live diff rows.

Use the normal local commands for the full private dashboard:

```powershell
pnpm dev
pnpm build
```

Keep the project source repository private if it contains full `src/data` forecast payloads. The public build protects the Vercel deployment bundle; it does not make a public Git repository safe by itself.
