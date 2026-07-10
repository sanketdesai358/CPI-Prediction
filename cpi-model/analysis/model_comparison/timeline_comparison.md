# Headline Model Timeline Comparison

Every prediction is sourced from existing walk-forward artifacts; no models were retrained.

Y/y = 11 actual months + 1 forecast month.

## Model availability

| Model | Start | End | Months | Full SA m/m MAE | Full SA y/y MAE | Common 2022+ SA m/m MAE | Common 2022+ SA y/y MAE |
|---|---|---|---:|---:|---:|---:|---:|
| Production Tier 1 fallback | 2015-06 | 2026-05 | 131 | 0.144% | 0.147% | 0.116% | 0.121% |
| Production Tier 3 fallback | 2015-06 | 2026-05 | 131 | 0.138% | 0.141% | 0.108% | 0.113% |
| HRNN | 2017-07 | 2026-05 | 105 | 0.126% | 0.131% | 0.120% | 0.126% |
| I-GRU | 2017-07 | 2026-05 | 105 | 0.125% | 0.129% | 0.116% | 0.121% |
| Challenger Seasonal AR | 2017-07 | 2026-05 | 105 | 0.117% | 0.121% | 0.107% | 0.112% |

## Notes

- Production Tier 1 and Tier 3 fallback lines are walk-forward leaf-aggregated baselines. SETB01 gasoline uses the cached EIA weekly regular gasoline calendar-month pass-through when available; all other components use the stated CPI-history fallback formulas. They do not include other live-feed overrides such as Manheim used vehicles, jet fuel, shelter rent overlays, or food feed scaffolding.
- Existing challenger/hrnn/results.json starts at 2017-07; no ~2000 challenger prediction rows are present. Regenerate challenger/hrnn/results.json from an artifact with earlier BLS history to extend the line.
- The full production model is still omitted. The existing backtest/C/results.json series is a headline history scaffold, not a replay of the full production tier forecast with component live feeds. The only real production forecast artifact currently present is the current 2026-06 run, which is too short for a historical comparison. Build monthly forecast.py snapshots using only as-of data to add a true production line.
