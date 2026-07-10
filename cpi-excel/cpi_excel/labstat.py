from __future__ import annotations

import io
import json
import re
from pathlib import Path
from typing import Any

import pandas as pd

from .constants import BASE_URLS, LABSTAT_DIR
from .sources import download_text


def _read_tsv(text: str) -> pd.DataFrame:
    df = pd.read_csv(io.StringIO(text), sep="\t", dtype=str, keep_default_na=False)
    df.columns = [column.strip() for column in df.columns]
    for column in df.columns:
        df[column] = df[column].astype(str).str.strip()
    return df


def load_items(*, force: bool = False) -> pd.DataFrame:
    text = download_text(BASE_URLS["cu_item"], LABSTAT_DIR / "cu.item", force=force)
    df = _read_tsv(text)
    df["display_level"] = pd.to_numeric(df["display_level"], errors="coerce").fillna(0).astype(int)
    df["sort_sequence"] = pd.to_numeric(df["sort_sequence"], errors="coerce").fillna(0).astype(int)
    return df.sort_values(["sort_sequence", "item_code"]).reset_index(drop=True)


def load_series(*, force: bool = False) -> pd.DataFrame:
    text = download_text(BASE_URLS["cu_series"], LABSTAT_DIR / "cu.series", force=force)
    df = _read_tsv(text)
    df["series_id"] = df["series_id"].str.strip()
    for column in ("begin_year", "end_year"):
        df[column] = pd.to_numeric(df[column], errors="coerce")
    return df


def us_city_monthly_cpiu_series(series_df: pd.DataFrame) -> pd.DataFrame:
    return series_df[
        (series_df["area_code"] == "0000")
        & (series_df["periodicity_code"] == "R")
        & (series_df["series_id"].str.startswith("CU"))
        & (series_df["series_id"].str[2].isin(["S", "U"]))
    ].copy()


def infer_parent_map(items_df: pd.DataFrame) -> dict[str, str | None]:
    parent_by_code: dict[str, str | None] = {}
    stack: list[tuple[int, str]] = []

    for row in items_df.itertuples(index=False):
        code = str(row.item_code)
        level = int(row.display_level)
        name = str(row.item_name)

        while stack and stack[-1][0] >= level:
            stack.pop()

        parent = stack[-1][1] if stack else None
        if parent is None and code != "SA0" and not name.lower().startswith("purchasing power"):
            parent = "SA0"

        parent_by_code[code] = parent
        stack.append((level, code))

    return parent_by_code


def infer_leaf_map(items_df: pd.DataFrame) -> dict[str, bool]:
    rows = list(items_df.itertuples(index=False))
    leaf_by_code: dict[str, bool] = {}
    for index, row in enumerate(rows):
        level = int(row.display_level)
        has_child = False
        for later in rows[index + 1 :]:
            later_level = int(later.display_level)
            if later_level <= level:
                break
            has_child = True
            break
        leaf_by_code[str(row.item_code)] = not has_child
    return leaf_by_code


FACTSHEET_LINKS: dict[str, str] = {
    "SETB01": "https://www.bls.gov/cpi/factsheets/gasoline.htm",
    "SEHF01": "https://www.bls.gov/cpi/factsheets/electricity.htm",
    "SEHA": "https://www.bls.gov/cpi/factsheets/owners-equivalent-rent-and-rent.htm",
    "SEHC": "https://www.bls.gov/cpi/factsheets/owners-equivalent-rent-and-rent.htm",
    "SETA01": "https://www.bls.gov/cpi/factsheets/new-vehicles.htm",
    "SETA02": "https://www.bls.gov/cpi/factsheets/used-cars-and-trucks.htm",
    "SETE": "https://www.bls.gov/cpi/factsheets/motor-vehicle-insurance.htm",
    "SETG01": "https://www.bls.gov/cpi/factsheets/airline-fares.htm",
    "SAM": "https://www.bls.gov/cpi/factsheets/medical-care.htm",
    "SEME": "https://www.bls.gov/cpi/factsheets/health-insurance.htm",
    "SEEB01": "https://www.bls.gov/cpi/factsheets/college-tuition.htm",
    "SAF11": "https://www.bls.gov/cpi/factsheets/average-food-prices.htm",
}


METHODOLOGY_OVERRIDES: dict[str, dict[str, str]] = {
    "SA0": {"formula": "aggregate", "collection": "aggregate", "qa_method": "aggregate", "alt_data": ""},
    "SA0L1E": {"formula": "aggregate", "collection": "aggregate", "qa_method": "aggregate", "alt_data": ""},
    "SAF1": {"formula": "aggregate", "collection": "aggregate", "qa_method": "aggregate", "alt_data": ""},
    "SAF11": {
        "formula": "GM",
        "collection": "direct collection; monthly in all areas",
        "qa_method": "cell-relative imputation common; seasonal-item pricing rules",
        "alt_data": "",
    },
    "SAF111": {"formula": "GM", "collection": "monthly", "qa_method": "cell-relative", "alt_data": ""},
    "SAF112": {"formula": "GM", "collection": "monthly", "qa_method": "cell-relative", "alt_data": ""},
    "SEFJ": {"formula": "GM", "collection": "monthly", "qa_method": "cell-relative", "alt_data": ""},
    "SAF113": {"formula": "GM", "collection": "monthly", "qa_method": "cell-relative", "alt_data": ""},
    "SAF114": {"formula": "GM", "collection": "monthly", "qa_method": "cell-relative", "alt_data": ""},
    "SAF115": {"formula": "GM", "collection": "monthly", "qa_method": "cell-relative", "alt_data": ""},
    "SEFV": {"formula": "GM", "collection": "monthly", "qa_method": "slow wage/input pass-through", "alt_data": ""},
    "SAF116": {"formula": "GM", "collection": "mixed", "qa_method": "BLS direct quality adjustment/imputation as applicable", "alt_data": ""},
    "SA0E": {"formula": "aggregate", "collection": "aggregate", "qa_method": "aggregate", "alt_data": ""},
    "SETB01": {
        "formula": "GM",
        "collection": "secondary-source transaction dataset; full-month coverage",
        "qa_method": "direct comparison",
        "alt_data": "secondary-source transaction dataset since June 2021 indexes",
    },
    "SEHE01": {"formula": "GM", "collection": "monthly", "qa_method": "BLS direct quality adjustment/imputation as applicable", "alt_data": ""},
    "SEHF01": {
        "formula": "ML",
        "collection": "monthly utility pricing",
        "qa_method": "regulated-price carry-forward where applicable",
        "alt_data": "",
    },
    "SEHF02": {
        "formula": "ML",
        "collection": "monthly utility pricing",
        "qa_method": "regulated-price carry-forward where applicable",
        "alt_data": "",
    },
    "SAH1": {"formula": "aggregate", "collection": "aggregate", "qa_method": "aggregate", "alt_data": ""},
    "SEHA": {
        "formula": "6MR",
        "collection": "Housing survey: six rotating panels; units priced twice per year",
        "qa_method": "age-bias adjustment; donor imputation for missed collections",
        "alt_data": "",
    },
    "SEHC": {
        "formula": "6MR",
        "collection": "same renter sample, reweighted to owner stock",
        "qa_method": "age-bias adjustment; donor imputation for missed collections",
        "alt_data": "",
    },
    "SEHB": {"formula": "GM", "collection": "monthly", "qa_method": "BLS direct quality adjustment/imputation as applicable", "alt_data": ""},
    "SEHG": {
        "formula": "ML",
        "collection": "monthly/bimonthly government and utility fees",
        "qa_method": "carry-forward for regulated prices where applicable",
        "alt_data": "",
    },
    "SAH3": {
        "formula": "GM",
        "collection": "bimonthly outside New York/Los Angeles/Chicago",
        "qa_method": "hedonics for selected appliances; BLS imputation as applicable",
        "alt_data": "",
    },
    "SAA": {
        "formula": "GM",
        "collection": "bimonthly outside New York/Los Angeles/Chicago",
        "qa_method": "hedonics and class-mean imputation; seasonal-item pricing rules",
        "alt_data": "",
    },
    "SAT": {"formula": "aggregate", "collection": "aggregate", "qa_method": "aggregate", "alt_data": ""},
    "SETA01": {
        "formula": "GM",
        "collection": "J.D. Power transaction data",
        "qa_method": "cost-based quality adjustment; class-mean imputation at model-year changeover",
        "alt_data": "J.D. Power transaction data since April 2022 indexes",
    },
    "SETA02": {
        "formula": "GM",
        "collection": "J.D. Power Valuation Services data",
        "qa_method": "depreciation adjustment plus inherited new-vehicle quality adjustment",
        "alt_data": "J.D. Power Valuation Services data",
    },
    "SETC": {"formula": "GM", "collection": "bimonthly", "qa_method": "BLS direct quality adjustment/imputation as applicable", "alt_data": ""},
    "SETB": {"formula": "aggregate", "collection": "see gasoline", "qa_method": "aggregate", "alt_data": "see gasoline"},
    "SETD": {"formula": "GM", "collection": "bimonthly", "qa_method": "BLS direct quality adjustment/imputation as applicable", "alt_data": ""},
    "SETE": {
        "formula": "GM",
        "collection": "premium quotes for fixed risk profiles; filings can be lumpy",
        "qa_method": "carry-forward between filings where applicable",
        "alt_data": "",
    },
    "SETG01": {
        "formula": "GM",
        "collection": "verify current source on BLS factsheet",
        "qa_method": "directional fare mix rules; BLS imputation as applicable",
        "alt_data": "verify - factsheet",
    },
    "SAM": {"formula": "aggregate", "collection": "aggregate", "qa_method": "aggregate", "alt_data": ""},
    "SAM1": {"formula": "GM", "collection": "monthly/mixed", "qa_method": "BLS direct quality adjustment/imputation as applicable", "alt_data": "verify prescription-drug source on factsheet"},
    "SEMC01": {"formula": "GM/ML elements", "collection": "claims-based reimbursement pricing", "qa_method": "BLS imputation as applicable", "alt_data": ""},
    "SEMD01": {"formula": "ML elements", "collection": "monthly", "qa_method": "BLS imputation as applicable", "alt_data": ""},
    "SEME": {
        "formula": "indirect retained-earnings method",
        "collection": "annual insurer financial data incorporated on a lagged cycle",
        "qa_method": "method-specific retained-earnings calculation",
        "alt_data": "verify current retained-earnings cadence on factsheet",
    },
    "SAR": {"formula": "GM", "collection": "bimonthly outside New York/Los Angeles/Chicago", "qa_method": "hedonics for TVs/audio where applicable", "alt_data": ""},
    "SAE": {"formula": "aggregate", "collection": "aggregate", "qa_method": "aggregate", "alt_data": ""},
    "SEEB01": {"formula": "GM", "collection": "annual repricing concentrated in Aug-Sep", "qa_method": "BLS direct quality adjustment/imputation as applicable", "alt_data": ""},
    "SEED03": {
        "formula": "GM",
        "collection": "secondary-source plan-offer plus expenditure data",
        "qa_method": "hedonic imputation",
        "alt_data": "secondary-source plan-offer plus expenditure data since July 2025 indexes",
    },
    "SEEE03": {"formula": "GM", "collection": "web collection", "qa_method": "hedonics", "alt_data": ""},
    "SEEE04": {"formula": "GM", "collection": "directed substitution since 2018", "qa_method": "hedonics", "alt_data": ""},
    "SAG": {"formula": "aggregate", "collection": "aggregate", "qa_method": "aggregate", "alt_data": ""},
    "SEGA": {"formula": "GM", "collection": "monthly", "qa_method": "BLS direct quality adjustment/imputation as applicable", "alt_data": ""},
    "SAG1": {"formula": "GM", "collection": "bimonthly", "qa_method": "BLS direct quality adjustment/imputation as applicable", "alt_data": ""},
}


def _infer_formula(code: str, name: str, is_leaf: bool) -> str:
    if code in METHODOLOGY_OVERRIDES:
        return METHODOLOGY_OVERRIDES[code]["formula"]
    lname = name.lower()
    if not is_leaf or code.startswith("SA") or code in {"SAC", "SAS", "SAD", "SAN"}:
        return "aggregate"
    if code in {"SEHA", "SEHC", "SEHC01"}:
        return "6MR"
    if code.startswith(("SEHF", "SEHG")) or code.startswith("SS57"):
        return "ML"
    if "insurance" in lname and code == "SEME":
        return "indirect retained-earnings method"
    return "GM"


def _infer_collection(code: str, name: str, formula: str) -> str:
    if code in METHODOLOGY_OVERRIDES:
        return METHODOLOGY_OVERRIDES[code]["collection"]
    if formula == "aggregate":
        return "aggregate"
    if code.startswith(("SEF", "SSF")) or "food" in name.lower():
        return "monthly food collection where sampled"
    if code.startswith(("SETB", "SEHE", "SEHF")) or "gasoline" in name.lower():
        return "monthly energy/utility collection"
    if code.startswith(("SEHA", "SEHB", "SEHC", "SEHD", "SEHG")):
        return "monthly/six-panel shelter or housing-service collection"
    return "monthly in New York/Los Angeles/Chicago; often bimonthly elsewhere"


def _infer_qa_method(code: str, name: str, formula: str) -> str:
    if code in METHODOLOGY_OVERRIDES:
        return METHODOLOGY_OVERRIDES[code]["qa_method"]
    lname = name.lower()
    if formula == "aggregate":
        return "aggregate of component methods"
    if code.startswith(("SEHA", "SEHC")):
        return "age-bias adjustment; donor imputation for missed collections"
    if any(term in lname for term in ("vehicle", "cars", "trucks")):
        return "cost/depreciation quality adjustment and class-mean imputation as applicable"
    if any(term in lname for term in ("television", "computer", "internet", "telephone", "smartphone")):
        return "hedonic quality adjustment or hedonic imputation where applicable"
    if "apparel" in lname or code.startswith(("SEA", "SSA")):
        return "hedonics/class-mean imputation; seasonal-item rules where applicable"
    return "cell-relative imputation for missing quotes; direct comparison/direct QA as applicable"


def _infer_alt_data(code: str) -> str:
    if code in METHODOLOGY_OVERRIDES:
        return METHODOLOGY_OVERRIDES[code]["alt_data"]
    return ""


def _methodology_links(code: str, series_nsa: str | None, series_sa: str | None) -> list[str]:
    links = [
        BASE_URLS["handbook_calculation"],
        BASE_URLS["handbook_data"],
        BASE_URLS["quality_adjustment"],
    ]
    factsheet = FACTSHEET_LINKS.get(code, BASE_URLS["factsheets"])
    links.insert(0, factsheet)
    if series_nsa:
        links.append(f"https://data.bls.gov/timeseries/{series_nsa}")
    if series_sa:
        links.append(f"https://data.bls.gov/timeseries/{series_sa}")
    return list(dict.fromkeys(links))


def build_registry(items_df: pd.DataFrame, series_df: pd.DataFrame) -> list[dict[str, Any]]:
    us_series = us_city_monthly_cpiu_series(series_df)
    nsa = {
        row.item_code: row.series_id
        for row in us_series[us_series["seasonal"] == "U"].itertuples(index=False)
    }
    sa = {
        row.item_code: row.series_id
        for row in us_series[us_series["seasonal"] == "S"].itertuples(index=False)
    }
    parent_map = infer_parent_map(items_df)
    leaf_map = infer_leaf_map(items_df)

    registry: list[dict[str, Any]] = []
    for row in items_df.itertuples(index=False):
        code = str(row.item_code)
        if str(row.selectable).upper() != "T":
            continue
        if code not in nsa:
            continue
        name = str(row.item_name)
        is_leaf = bool(leaf_map.get(code, True))
        formula = _infer_formula(code, name, is_leaf)
        series_nsa = nsa.get(code)
        series_sa = sa.get(code)
        registry.append(
            {
                "name": name,
                "item_code": code,
                "series_nsa": series_nsa,
                "series_sa": series_sa,
                "parent": parent_map.get(code),
                "level": int(row.display_level),
                "display_level": int(row.display_level),
                "sort_sequence": int(row.sort_sequence),
                "is_item_stratum": is_leaf,
                "formula": formula,
                "collection": _infer_collection(code, name, formula),
                "qa_method": _infer_qa_method(code, name, formula),
                "alt_data": _infer_alt_data(code),
                "links": _methodology_links(code, series_nsa, series_sa),
                "notes": "Generated from BLS cu.item/cu.series; methodology defaults are overridden where SPEC.md identifies component-specific methods.",
                "source": {
                    "item": BASE_URLS["cu_item"],
                    "series": BASE_URLS["cu_series"],
                    "methodology_spec": "SPEC.md section 3",
                },
            }
        )
    return sorted(registry, key=lambda item: (item["sort_sequence"], item["item_code"]))


def validate_registry(
    registry: list[dict[str, Any]], items_df: pd.DataFrame, series_df: pd.DataFrame
) -> list[str]:
    errors: list[str] = []
    items = {row.item_code: row.item_name for row in items_df.itertuples(index=False)}
    series_ids = {row.series_id.strip() for row in series_df.itertuples(index=False)}

    for entry in registry:
        code = entry["item_code"]
        if code not in items:
            errors.append(f"{code}: item_code not found in cu.item")
            continue
        if entry["name"] != items[code]:
            errors.append(
                f"{code}: registry name {entry['name']!r} does not match cu.item {items[code]!r}"
            )
        for key in ("series_nsa", "series_sa"):
            series_id = entry.get(key)
            if series_id and series_id not in series_ids:
                errors.append(f"{code}: {key} {series_id} not found in cu.series")
    return errors


def write_registry(registry: list[dict[str, Any]], path: Path) -> None:
    path.write_text(json.dumps(registry, indent=2, sort_keys=False), encoding="utf-8")


def read_registry(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_item_name(name: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", " ", name.lower()).strip()
    replacements = {
        "owners equivalent rent of residences": "owners equivalent rent of residences",
        "owners equivalent rent of primary residence": "owners equivalent rent of primary residence",
    }
    return replacements.get(cleaned, cleaned)
