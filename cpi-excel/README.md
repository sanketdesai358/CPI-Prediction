# CPI Component Workbook

Builds `cpi_component_workbook.xlsx`, an auditable CPI-U component workbook for the U.S. city average.

The pipeline reads `SPEC.md`, downloads BLS LABSTAT metadata (`cu.item`, `cu.series`), validates the generated component registry, pulls CPI index history from the BLS API, and writes Excel formulas for:

- SA m/m %
- NSA y/y %
- price-updated relative importance
- approximate contribution to all-items m/m change

## Setup

```powershell
python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:BLS_API_KEY = "your-key"
python build_workbook.py
pytest
```

Register a free BLS API key at https://data.bls.gov/registrationEngine/.

If `BLS_API_KEY` is absent, the builder uses the lower unregistered API batch size and can fall back to the LABSTAT `cu.data.0.Current` flat file. All `download.bls.gov` requests send a real User-Agent; override it with:

```powershell
$env:BLS_USER_AGENT = "Your Name your.email@example.com"
```

## Refresh

Run:

```powershell
BLS_API_KEY=... python build_workbook.py --force-refresh
```

Raw responses are cached under `data/raw/`:

- `data/raw/labstat/` for flat files
- `data/raw/api/` for BLS API JSON batches
- `data/raw/cpi-relative-importance.xlsx` for the current RI workbook

Delete the cache or use `--force-refresh` to force a clean pull.

## API Limits

BLS API v2 limits are 500 queries/day, 50 series/query, and 20 years/query with a key. This workbook fetches one six-year window for the registry series, batched at 50 series when a key is present and 25 series otherwise.

## Workbook

Sheets are:

`README`, `Dashboard`, `Component_Tree`, `Methodology`, `Weights`, `Latest_3M`, `Series_Catalog`, `Data_NSA`, `Data_SA`, `Sources`.

Conventions:

- Blue font: BLS/source inputs and hardcoded metadata.
- Black font: formulas.
- Green underlined font: hyperlinks.
- Negative numbers use parentheses.
- Metadata cells include comments with BLS source URLs.

`Latest_3M` and `Weights` contain formula-driven calculations referencing `Data_NSA` and `Data_SA`.

## Tests

```powershell
pytest
```

Coverage:

- registry validates against `cu.item` and `cu.series`
- BLS relative-importance worked example reproduces the published result
- major-group contribution sum reconciles to headline m/m within 0.05 percentage point
- all-items latest release-table values match BLS news table values

## Notes

LibreOffice/`soffice` is used for headless recalculation if available. If it is not installed, the builder still scans workbook formulas for literal Excel error tokens and marks the workbook for full recalculation on open.
