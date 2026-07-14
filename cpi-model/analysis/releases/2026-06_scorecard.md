# June 2026 CPI Post-Release Scorecard

Release date: July 14, 2026  
Forecast month: June 2026  
Scoring basis: archived pre-release forecast, SA contribution errors in percentage points.

## Release Verification

The refreshed BLS store contains the June release across the 400-component registry. The headline SA m/m is **-0.422%** and core SA m/m is **-0.017%**, matching the published release rounded to **-0.4%** and **0.0%**. Headline NSA m/m is **-0.349%** and core NSA m/m is **+0.011%**. Source: [BLS June 2026 CPI release](https://www.bls.gov/news.release/archives/cpi_07142026.htm).

## Headline And Core Model Scores

Values are percent m/m; errors are prediction minus actual in basis points. The two production rows are the requested Tier 1 and Tier 3 fallback variants. The HRNN, I-GRU, and Challenger Seasonal AR values are the precomputed challenger one-step-ahead values for June.

| Model | Headline SA m/m | Error bp | Headline NSA m/m | Error bp | Core SA m/m | Error bp | Core NSA m/m | Error bp |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Actual | -0.422% | - | -0.349% | - | -0.017% | - | +0.011% | - |
| Production Tier 1 fallback | -0.182% | +24.1 | -0.103% | +24.6 | +0.291% | +30.8 | +0.322% | +31.1 |
| Production Tier 3 fallback | -0.178% | +24.5 | -0.099% | +25.0 | +0.289% | +30.6 | +0.319% | +30.8 |
| HRNN | -0.137% | +28.6 | -0.058% | +29.1 | +0.385% | +40.2 | +0.415% | +40.5 |
| I-GRU | -0.192% | +23.1 | -0.113% | +23.8 | +0.289% | +30.5 | +0.319% | +30.8 |
| Challenger Seasonal AR | -0.130% | +29.2 | -0.051% | +29.8 | +0.303% | +32.0 | +0.333% | +32.3 |

**Monthly winner:** I-GRU has the smallest headline SA and NSA m/m error, and is narrowly best on core SA. Tier 3 is narrowly best on core NSA. All models missed the unusually soft June core print by forecasting a positive core m/m.

## Implied Y/Y

The nowcaster convention is 11 known actual months plus the model's June forecast month. Actual headline SA y/y was **3.464%** and NSA y/y **3.531%**. Actual core SA y/y was **2.566%** and NSA y/y **2.594%**.

| Model | Headline SA y/y | Error bp | Headline NSA y/y | Error bp | Core SA y/y | Error bp | Core NSA y/y | Error bp |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Production Tier 1 fallback | 3.714% | +25.0 | 3.787% | +25.6 | 2.882% | +31.6 | 2.913% | +31.9 |
| Production Tier 3 fallback | 3.718% | +25.4 | 3.792% | +26.0 | 2.879% | +31.3 | 2.911% | +31.7 |
| HRNN | 3.760% | +29.7 | 3.834% | +30.3 | 3.010% | +44.4 | 3.041% | +44.7 |
| I-GRU | 3.703% | +24.0 | 3.777% | +24.6 | 2.879% | +31.3 | 2.911% | +31.7 |
| Challenger Seasonal AR | 3.767% | +30.4 | 3.841% | +31.0 | 2.925% | +35.9 | 2.956% | +36.2 |

## Production Deep Dive

| Component | Forecast SA m/m | Actual SA m/m | Error | Status | Reading |
|---|---:|---:|---:|---|---|
| Gasoline | -9.216% | -9.687% | +4.7 bp | Live EIA | EIA weekly calendar-month average gave the direction and was close; timing/seasonal conversion explains the residual. |
| Lodging away from home | +1.371% | -2.323% | +369.3 bp | Live CoStar/STR | ADR rose with the World Cup host-city mix, but the national CPI lodging print fell. The ADR pass-through treated a mix shock as a fixed-room price signal. |
| Motor vehicle insurance | -0.755% | -2.006% | +125.1 bp | Licensed-feed fallback | No licensed filing feed was available; the Seasonal AR fallback missed the unusually large decline. |
| OER residences | +0.292% | +0.240% | +5.2 bp | Tier 1 CPI fallback | Close; Zillow/rent overlay was not used. |
| Rent primary residence | +0.323% | +0.150% | +17.3 bp | Tier 1 CPI fallback | Direction was right, but the CPI persistence/seasonal blend was too high. |
| Used cars and trucks | -0.197% | -0.230% | +3.3 bp | Live Manheim | Manheim m0/m2 signal was directionally useful and close after the SA/NSA conversion. |

For lodging, the old production Seasonal AR would have predicted **+2.564% NSA m/m** for June; the ADR-primary model predicted **+2.028% NSA m/m**. Both missed the actual **-2.532% NSA m/m**, so the ADR switch did not improve this release. The ADR model's June headline contribution was about **0.055 pp above actual** on the SA scoring basis.

## Top Ten Contribution Errors

| Rank | Component | SA contribution error | Diagnosis |
|---:|---|---:|---|
| 1 | Communication | +0.068 pp | Seasonal partial-pooling fallback forecast a positive print; actual was a sharp decline. |
| 2 | Lodging away from home | +0.055 pp | ADR/World Cup mix signal was not representative of CPI's fixed-room sample. |
| 3 | Airline fares | +0.037 pp | Generic airfare proxy plus guarded jet-fuel pass-through overestimated the CPI move. |
| 4 | Motor vehicle insurance | +0.033 pp | Licensed-only feed gap forced an AR fallback during a large negative print. |
| 5 | Household furnishings | -0.030 pp | Seasonal AR partial-pooling missed a positive actual. |
| 6 | Gasoline | +0.020 pp | EIA input was close; remaining error is pass-through/SA timing. |
| 7 | Professional services | +0.018 pp | Partial-pooling fallback expected positive momentum; actual was slightly negative. |
| 8 | Other motor fuels | +0.016 pp | Seasonal fallback did not capture the sharp energy reversal. |
| 9 | Car and truck rental | -0.016 pp | Proxy/fallback missed a large positive actual. |
| 10 | Fuel oil | +0.015 pp | Feed was present, but the CPI timing/pass-through signal moved opposite the print. |

## Honesty And Archive Checks

- All 128 forecast components had June actuals and were scored; no component actual was missing.
- The scored forecast is the pre-release archived artifact from `cpi-model-archive/runs/2026-06_rev3/`, exported July 13, before the July 14 BLS release. It was not regenerated from June actuals.
- The archive contains 128 component predictions for each of Production, HRNN, I-GRU, and Seasonal AR. The score table separately identifies live-feed rows and explicit fallbacks.
- Four scored production rows carried an explicit feed fallback; the most important is motor vehicle insurance (`licensed_only_fallback`). Gasoline, used cars, and lodging were live-feed rows for this run.
- The regenerated comparison artifacts now include June for the production fallback lines and the pre-release HRNN, I-GRU, and Seasonal AR current-forecast values. Historical walk-forward lines remain unchanged and are not retroactively refit.
