# CoStar/STR ADR lodging model

Public cache span: 2022-03-31 to 2026-07-09; 130 weekly and 31 monthly releases parsed.

## Window C walk-forward (common available span)

| Model | Months | MAE | RMSE |
|---|---:|---:|---:|
| CoStar ADR primary | 13 | 2.111% | 2.522% |
| Old Seasonal AR | 13 | 1.704% | 2.380% |

## June 2026

- CoStar ADR primary lodging NSA m/m: 2.028%
- Old production Seasonal AR (`SEHB`) NSA m/m: 2.564%
- Narrow hotels/motels Seasonal AR (`SEHB02`) NSA m/m: 3.001%
- Headline contribution difference: -0.008 pp
- Driver: CoStar/STR ADR primary: 2026-06 weekly-derived $173.89 vs 2026-05 official $168.51 (+3.19%); 5 weekly prints, 0 carried days; pass-through +2.03%

June actual remains pending until the July 14, 2026 CPI release and should then be scored through the archive scorer.

## Honesty notes

- Direct scripted requests currently receive HTTP 403; the feed uses cached public browser-rendered releases and reports refresh failures in feed health.
- The public listing exposes unique parsed publications from March 2022 onward and official monthly levels from October 2023 onward. Older advertised filter years are not claimed as recovered.
- ADR is a mix-weighted average room revenue measure; CPI holds room specifications more nearly fixed. A low fitted beta is therefore plausible.
- Official monthly ADR is used for training when published; weekly day-weighted ADR is used for the unpublished current month.
