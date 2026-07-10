from __future__ import annotations

from pathlib import Path

BASE_URLS = {
    "bls_api": "https://api.bls.gov/publicAPI/v2/timeseries/data/",
    "api_registration": "https://data.bls.gov/registrationEngine/",
    "labstat_base": "https://download.bls.gov/pub/time.series/cu/",
    "cu_item": "https://download.bls.gov/pub/time.series/cu/cu.item",
    "cu_series": "https://download.bls.gov/pub/time.series/cu/cu.series",
    "cu_current": "https://download.bls.gov/pub/time.series/cu/cu.data.0.Current",
    "relative_importance": "https://www.bls.gov/cpi/tables/relative-importance/",
    "relative_importance_xlsx": "https://www.bls.gov/web/cpi/cpi-relative-importance.xlsx",
    "news_release": "https://www.bls.gov/news.release/cpi.nr0.htm",
    "news_table_1": "https://www.bls.gov/news.release/cpi.t01.htm",
    "news_table_2": "https://www.bls.gov/news.release/cpi.t02.htm",
    "supplemental": "https://www.bls.gov/web/cpi.supp.toc.htm",
    "release_calendar": "https://www.bls.gov/schedule/news_release/cpi.htm",
    "handbook_design": "https://www.bls.gov/opub/hom/cpi/design.htm",
    "handbook_data": "https://www.bls.gov/opub/hom/cpi/data.htm",
    "handbook_calculation": "https://www.bls.gov/opub/hom/cpi/calculation.htm",
    "factsheets": "https://www.bls.gov/cpi/factsheets/",
    "quality_adjustment": "https://www.bls.gov/cpi/quality-adjustment/",
    "seasonal_adjustment": "https://www.bls.gov/cpi/seasonal-adjustment/",
    "weight_update_2026": "https://www.bls.gov/cpi/tables/relative-importance/weight-update-comparison-2026.htm",
    "cost_weights": "https://www.bls.gov/cpi/tables/consumer-expenditure/cost-weights.htm",
}

DEFAULT_USER_AGENT = (
    "CPI component workbook builder; contact: cpi-workbook@example.com"
)

DATA_DIR = Path("data")
RAW_DIR = DATA_DIR / "raw"
LABSTAT_DIR = RAW_DIR / "labstat"
API_DIR = RAW_DIR / "api"

WORKBOOK_FILENAME = "cpi_component_workbook.xlsx"
REGISTRY_FILENAME = "registry.json"

FORMULA_ERROR_TOKENS = ("#REF!", "#DIV/0!", "#VALUE!", "#N/A", "#NAME?", "#NUM!", "#NULL!")

