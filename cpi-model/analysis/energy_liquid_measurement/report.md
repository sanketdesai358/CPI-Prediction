# EIA liquid-fuel measurement models

These models replace the CPI-history fallbacks for `SETB02` Other motor fuels and `SEHE01` Fuel oil. They use calendar-month EIA price measurements, following the gasoline model's timing discipline, with a zero-intercept retail pass-through coefficient estimated only from months before the forecast month.

## Sources and specification

| CPI component | Primary measurement | Frequency | Pass-through |
|---|---|---|---|
| Other motor fuels (`SETB02`) | EIA U.S. No. 2 diesel retail price | Weekly | As-of fitted beta, bounded 0.50-1.15 |
| Fuel oil (`SEHE01`) | EIA New York Harbor No. 2 heating oil spot price | Daily | As-of fitted beta, bounded 0.20-0.90 |

The monthly measurement is the arithmetic average of all observations dated in the target calendar month divided by the prior calendar month's average, minus one. If the EIA measurement is unavailable, the model explicitly falls back to the Tier 1 CPI-history formula and marks the feed fallback.

## Walk-forward results, July 2017 through June 2026

| Component | Months | Measurement model MAE | Measurement model RMSE | June fitted beta |
|---|---:|---:|---:|---:|
| Other motor fuels | 106 | 0.934% | 1.370% | 0.909 |
| Fuel oil | 106 | 2.394% | 3.152% | 0.502 |

## June 2026 counterfactual

| Component | Archived old forecast | New EIA model | Actual | Old absolute error | New absolute error |
|---|---:|---:|---:|---:|---:|
| Other motor fuels | +5.265% | -9.343% | -7.217% | 12.482 pp | 2.127 pp |
| Fuel oil | +3.509% | -6.611% | -9.252% | 12.761 pp | 2.641 pp |

The archived June forecast remains untouched. This table is a retrospective specification comparison; the new models apply to future forecast runs.
