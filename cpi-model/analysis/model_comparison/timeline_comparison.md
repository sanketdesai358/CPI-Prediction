# Headline Model Timeline Comparison

Every prediction is sourced from existing walk-forward artifacts; no models were retrained.

Y/y = 11 actual months + 1 forecast month.

## Model availability

| Model | Start | End | Months | Full SA m/m MAE | Full SA m/m RMSE | Full SA y/y MAE | Full SA y/y RMSE | Common 2022+ SA m/m MAE | Common SA m/m RMSE | Common SA y/y MAE | Common SA y/y RMSE |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Production Tier 1 fallback | 2015-07 | 2026-06 | 131 | 0.167% | 0.516% | 0.171% | 0.519% | 0.121% | 0.165% | 0.126% | 0.173% |
| Production Tier 3 fallback | 2015-07 | 2026-06 | 131 | 0.161% | 0.514% | 0.165% | 0.517% | 0.114% | 0.158% | 0.119% | 0.165% |
| HRNN | 2017-08 | 2026-06 | 105 | 0.127% | 0.174% | 0.132% | 0.181% | 0.124% | 0.173% | 0.129% | 0.181% |
| I-GRU | 2017-08 | 2026-06 | 105 | 0.125% | 0.170% | 0.130% | 0.176% | 0.118% | 0.160% | 0.123% | 0.167% |
| Challenger Seasonal AR | 2017-08 | 2026-06 | 105 | 0.119% | 0.172% | 0.124% | 0.180% | 0.111% | 0.152% | 0.117% | 0.161% |

## Notes

- Production Tier 1 and Tier 3 fallback lines are walk-forward leaf-aggregated baselines. SETB01 gasoline uses the cached EIA weekly regular gasoline calendar-month pass-through when available; all other components use the stated CPI-history fallback formulas. They do not include other live-feed overrides such as Manheim used vehicles, jet fuel, shelter rent overlays, or food feed scaffolding.
- Existing challenger/hrnn/results.json starts at 2017-08; no ~2000 challenger prediction rows are present. Regenerate challenger/hrnn/results.json from an artifact with earlier BLS history to extend the line.
- The full production model is still omitted. The existing backtest/C/results.json series is a headline history scaffold, not a replay of the full production tier forecast with component live feeds. The only real production forecast artifact currently present is the current 2026-06 run, which is too short for a historical comparison. Build monthly forecast.py snapshots using only as-of data to add a true production line.
