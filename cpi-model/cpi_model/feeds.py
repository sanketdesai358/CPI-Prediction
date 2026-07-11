from __future__ import annotations

import csv
import base64
import io
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd

from .cme_futures import collect_cme_futures, food_futures_lag_report
from .data import write_json
from .math import add_months
from .paths import ROOT, RUNS_DIR, WORKSPACE
from .used_vehicles import manheim_final_publication_date


USER_AGENT = "cpi-component-dashboard/0.3 (+local research; contact: sanketsdesai.1995@gmail.com)"
DATA_DIR = ROOT / "data"
FEED_CACHE_DIR = DATA_DIR / "feeds"
AAA_ARCHIVE_DIR = DATA_DIR / "aaa"
BUNDLED_SITE_PACKAGES = Path.home() / ".cache" / "codex-runtimes" / "codex-primary-runtime" / "dependencies" / "python" / "Lib" / "site-packages"
LIVE_STATUSES = {"live", "live_current_snapshot", "live_pdf_fallback"}

EIA_API = "https://api.eia.gov/v2"
FRED_API = "https://api.stlouisfed.org/fred/series/observations"
USDA_MNREPORTS = "https://www.ams.usda.gov/mnreports"
BLS_TIME_SERIES = "https://download.bls.gov/pub/time.series"

EIA_SERIES: dict[str, dict[str, Any]] = {
    "gasoline_regular": {
        "route": "petroleum/pri/gnd",
        "frequency": "weekly",
        "data": "value",
        "series": "EMM_EPMR_PTE_NUS_DPG",
        "label": "EIA weekly U.S. regular all-formulations retail gasoline",
        "unit": "dollars per gallon",
        "min": 0.5,
        "max": 8.0,
    },
    "gasoline_all_grades": {
        "route": "petroleum/pri/gnd",
        "frequency": "weekly",
        "data": "value",
        "series": "EMM_EPM0_PTE_NUS_DPG",
        "label": "EIA weekly U.S. all-grades retail gasoline",
        "unit": "dollars per gallon",
        "min": 0.5,
        "max": 8.0,
    },
    "diesel": {
        "route": "petroleum/pri/gnd",
        "frequency": "weekly",
        "data": "value",
        "series": "EMD_EPD2D_PTE_NUS_DPG",
        "label": "EIA weekly U.S. No. 2 diesel retail",
        "unit": "dollars per gallon",
        "min": 0.5,
        "max": 9.0,
    },
    "heating_oil": {
        "route": "petroleum/pri/spt",
        "frequency": "daily",
        "data": "value",
        "series": "EER_EPD2F_PF4_Y35NY_DPG",
        "label": "EIA New York Harbor No. 2 heating oil spot",
        "unit": "dollars per gallon",
        "min": 0.2,
        "max": 8.0,
    },
    "rbob": {
        "route": "petroleum/pri/spt",
        "frequency": "daily",
        "data": "value",
        "series": "EER_EPMRR_PF4_Y05LA_DPG",
        "label": "EIA Los Angeles RBOB regular gasoline spot",
        "unit": "dollars per gallon",
        "min": 0.2,
        "max": 8.0,
    },
    "wti": {
        "route": "petroleum/pri/spt",
        "frequency": "daily",
        "data": "value",
        "series": "RWTC",
        "label": "EIA Cushing WTI spot",
        "unit": "dollars per barrel",
        "min": -50.0,
        "max": 250.0,
    },
    "jet_fuel": {
        "route": "petroleum/pri/spt",
        "frequency": "daily",
        "data": "value",
        "series": "EER_EPJK_PF4_RGC_DPG",
        "label": "EIA Gulf Coast kerosene-type jet fuel spot",
        "unit": "dollars per gallon",
        "min": 0.2,
        "max": 8.0,
    },
    "henry_hub": {
        "route": "natural-gas/pri/fut",
        "frequency": "daily",
        "data": "value",
        "series": "RNGWHHD",
        "label": "EIA Henry Hub natural gas spot",
        "unit": "dollars per MMBtu",
        "min": 0.0,
        "max": 50.0,
    },
}

FRED_SERIES = {
    "DHHNGSP": "Henry Hub Natural Gas Spot Price",
    "DCOILWTICO": "WTI crude oil spot price",
}

TIER_FEEDS: dict[str, dict[str, Any]] = {
    "SETB01": {
        "name": "Gasoline (all types)",
        "tier": 1,
        "primary": "EIA weekly retail gasoline",
        "secondary": ["AAA daily national average gasoline", "EIA RBOB spot"],
        "unit": "dollars per gallon",
        "env": ["EIA_API_KEY"],
        "requires": ["gasoline_regular", "gasoline_all_grades", "rbob"],
    },
    "SEHE01": {
        "name": "Fuel oil",
        "tier": 1,
        "primary": "EIA heating oil spot",
        "secondary": ["EIA diesel"],
        "unit": "dollars per gallon",
        "env": ["EIA_API_KEY"],
        "requires": ["heating_oil", "diesel"],
    },
    "SEHF02": {
        "name": "Utility (piped) gas service",
        "tier": 1,
        "primary": "EIA Henry Hub",
        "secondary": ["FRED mirror"],
        "unit": "dollars per MMBtu",
        "env": ["EIA_API_KEY", "FRED_API_KEY"],
        "requires": ["henry_hub"],
    },
    "SEHF01": {
        "name": "Electricity",
        "tier": 1,
        "primary": "EIA retail electricity price",
        "secondary": [],
        "unit": "cents per kWh",
        "env": ["EIA_API_KEY"],
        "requires": ["electricity_residential"],
    },
    "SETA02": {
        "name": "Used cars and trucks",
        "tier": 1,
        "primary": "Manheim Used Vehicle Value Index",
        "secondary": ["manual CSV override"],
        "unit": "index",
        "env": [],
        "requires": ["manheim"],
    },
    "SETA01": {
        "name": "New vehicles",
        "tier": 1,
        "primary": "public ATP proxy",
        "secondary": ["J.D. Power PIN if licensed"],
        "unit": "index / price proxy",
        "env": [],
        "requires": [],
    },
    "SETG01": {
        "name": "Airline fares",
        "tier": 1,
        "primary": "EIA Gulf Coast jet fuel spot",
        "secondary": ["seasonal capacity pattern"],
        "unit": "dollars per gallon",
        "env": ["EIA_API_KEY"],
        "requires": ["jet_fuel"],
    },
    "SEME": {
        "name": "Health insurance",
        "tier": 2,
        "primary": "NAIC retained-earnings reports",
        "secondary": [],
        "unit": "retained earnings ratio",
        "env": [],
        "requires": [],
    },
    "SEEB01": {
        "name": "College tuition and fees",
        "tier": 2,
        "primary": "announced tuition data",
        "secondary": [],
        "unit": "event-month price change",
        "env": [],
        "requires": [],
    },
    "SETE": {
        "name": "Motor vehicle insurance",
        "tier": 2,
        "primary": "rate filings",
        "secondary": ["licensed filing tracker"],
        "unit": "premium filings",
        "env": [],
        "requires": [],
    },
    "FOOD_FUTURES": {
        "name": "Food futures basket",
        "tier": 1,
        "primary": "CME public chart-widget JSON endpoint",
        "secondary": ["Stooq fallback for blocked CME products", "ICE softs stay separate"],
        "unit": "futures settlement",
        "env": [],
        "requires": ["cme_futures"],
    },
    "SEFH": {
        "name": "Eggs",
        "tier": 1,
        "primary": "USDA weekly/daily shell egg reports",
        "secondary": ["BLS average-price validator", "APHIS HPAI layer shock"],
        "unit": "cents per dozen / retail dollars",
        "env": ["MARS_API_KEY", "BLS_API_KEY"],
        "requires": ["food_eggs", "bls_food_ap"],
    },
    "SEFC": {
        "name": "Beef and veal",
        "tier": 1,
        "primary": "USDA boxed beef cutout PM PDF",
        "secondary": ["BLS ground beef AP validator"],
        "unit": "dollars per cwt / retail dollars per lb",
        "env": ["MARS_API_KEY", "BLS_API_KEY"],
        "requires": ["food_beef_cutout", "bls_food_ap"],
    },
    "SEFD": {
        "name": "Pork",
        "tier": 1,
        "primary": "USDA pork cutout PM PDF",
        "secondary": ["BLS bacon AP validator"],
        "unit": "dollars per cwt / retail dollars per lb",
        "env": ["MARS_API_KEY", "BLS_API_KEY"],
        "requires": ["food_pork_cutout", "bls_food_ap"],
    },
    "SEFF": {
        "name": "Poultry",
        "tier": 1,
        "primary": "USDA weekly national chicken report",
        "secondary": ["BLS chicken AP validator", "APHIS HPAI broiler shock"],
        "unit": "cents per lb / retail dollars per lb",
        "env": ["MARS_API_KEY", "BLS_API_KEY"],
        "requires": ["food_chicken", "bls_food_ap"],
    },
    "SEFJ": {
        "name": "Dairy and related products",
        "tier": 1,
        "primary": "USDA NDPSR + federal milk order announcements",
        "secondary": ["BLS milk AP validator"],
        "unit": "dollars per lb / dollars per cwt",
        "env": ["MARS_API_KEY", "BLS_API_KEY"],
        "requires": ["food_dairy", "bls_food_ap"],
    },
    "SEFJ01": {
        "name": "Milk",
        "tier": 1,
        "primary": "USDA Class I advanced price",
        "secondary": ["BLS milk AP validator"],
        "unit": "dollars per cwt / retail dollars per gallon",
        "env": ["MARS_API_KEY", "BLS_API_KEY"],
        "requires": ["food_dairy", "bls_food_ap"],
    },
    "SEFJ02": {
        "name": "Cheese and related products",
        "tier": 1,
        "primary": "USDA NDPSR cheddar block price",
        "secondary": ["BLS dairy AP validators"],
        "unit": "dollars per lb",
        "env": ["MARS_API_KEY", "BLS_API_KEY"],
        "requires": ["food_dairy", "bls_food_ap"],
    },
    "SEFK": {
        "name": "Fresh fruits",
        "tier": 1,
        "primary": "USDA terminal-market produce basket",
        "secondary": ["BLS AP bananas validator"],
        "unit": "terminal market price / retail dollars",
        "env": ["MARS_API_KEY", "BLS_API_KEY"],
        "requires": ["food_produce", "bls_food_ap"],
    },
    "SEFL": {
        "name": "Fresh vegetables",
        "tier": 1,
        "primary": "USDA terminal-market produce basket",
        "secondary": ["BLS AP tomatoes/potatoes validators"],
        "unit": "terminal market price / retail dollars",
        "env": ["MARS_API_KEY", "BLS_API_KEY"],
        "requires": ["food_produce", "bls_food_ap"],
    },
    "SEFP01": {
        "name": "Coffee",
        "tier": 1,
        "primary": "Coffee futures / World Bank fallback",
        "secondary": ["BLS ground roast coffee AP validator"],
        "unit": "futures settlement / retail dollars per lb",
        "env": ["BLS_API_KEY"],
        "requires": ["futures", "bls_food_ap"],
    },
    "FOOD_HPAI": {
        "name": "APHIS HPAI layer/broiler shocks",
        "tier": 1,
        "primary": "APHIS public HPAI dashboard",
        "secondary": ["Tableau parser required"],
        "unit": "birds affected",
        "env": [],
        "requires": ["hpai"],
    },
    "FRED_MIRROR": {
        "name": "FRED mirror layer",
        "tier": 1,
        "primary": "FRED API",
        "secondary": list(FRED_SERIES.values()),
        "unit": "various",
        "env": ["FRED_API_KEY"],
        "requires": ["fred"],
    },
    "AAA_GAS": {
        "name": "AAA current-month gasoline",
        "tier": 1,
        "primary": "AAA daily national average gasoline",
        "secondary": [],
        "unit": "dollars per gallon",
        "env": [],
        "requires": ["aaa"],
    },
}

TIER_FEEDS.update(
    {
        "SEFD01": {
            "name": "Bacon, breakfast sausage, and related products",
            "tier": 1,
            "primary": "USDA pork cutout PM PDF",
            "secondary": ["BLS bacon AP validator"],
            "unit": "dollars per cwt / retail dollars per lb",
            "env": ["MARS_API_KEY", "BLS_API_KEY"],
            "requires": ["food_pork_cutout", "bls_food_ap"],
        },
        "SEFD02": {
            "name": "Ham",
            "tier": 1,
            "primary": "USDA pork cutout PM PDF",
            "secondary": [],
            "unit": "dollars per cwt",
            "env": ["MARS_API_KEY"],
            "requires": ["food_pork_cutout"],
        },
        "SEFD03": {
            "name": "Pork chops",
            "tier": 1,
            "primary": "USDA pork cutout PM PDF",
            "secondary": [],
            "unit": "dollars per cwt",
            "env": ["MARS_API_KEY"],
            "requires": ["food_pork_cutout"],
        },
        "SEFD04": {
            "name": "Other pork including roasts, steaks, and ribs",
            "tier": 1,
            "primary": "USDA pork cutout PM PDF",
            "secondary": [],
            "unit": "dollars per cwt",
            "env": ["MARS_API_KEY"],
            "requires": ["food_pork_cutout"],
        },
        "SEFC01": {
            "name": "Uncooked ground beef",
            "tier": 1,
            "primary": "USDA boxed beef cutout PM PDF",
            "secondary": ["BLS ground beef AP validator"],
            "unit": "dollars per cwt / retail dollars per lb",
            "env": ["MARS_API_KEY", "BLS_API_KEY"],
            "requires": ["food_beef_cutout", "bls_food_ap"],
        },
        "SEFC02": {
            "name": "Uncooked beef roasts",
            "tier": 1,
            "primary": "USDA boxed beef cutout PM PDF",
            "secondary": [],
            "unit": "dollars per cwt",
            "env": ["MARS_API_KEY"],
            "requires": ["food_beef_cutout"],
        },
        "SEFC03": {
            "name": "Uncooked beef steaks",
            "tier": 1,
            "primary": "USDA boxed beef cutout PM PDF",
            "secondary": [],
            "unit": "dollars per cwt",
            "env": ["MARS_API_KEY"],
            "requires": ["food_beef_cutout"],
        },
        "SEFC04": {
            "name": "Uncooked other beef and veal",
            "tier": 1,
            "primary": "USDA boxed beef cutout PM PDF",
            "secondary": [],
            "unit": "dollars per cwt",
            "env": ["MARS_API_KEY"],
            "requires": ["food_beef_cutout"],
        },
        "SEFF01": {
            "name": "Chicken",
            "tier": 1,
            "primary": "USDA weekly national chicken report",
            "secondary": ["BLS chicken AP validator", "APHIS HPAI broiler shock"],
            "unit": "cents per lb / retail dollars per lb",
            "env": ["MARS_API_KEY", "BLS_API_KEY"],
            "requires": ["food_chicken", "bls_food_ap"],
        },
        "SEFF02": {
            "name": "Other uncooked poultry including turkey",
            "tier": 1,
            "primary": "USDA weekly national chicken report",
            "secondary": ["APHIS HPAI broiler shock"],
            "unit": "cents per lb",
            "env": ["MARS_API_KEY"],
            "requires": ["food_chicken"],
        },
        "SEFJ03": {
            "name": "Ice cream and related products",
            "tier": 1,
            "primary": "USDA NDPSR + federal milk order announcements",
            "secondary": [],
            "unit": "dollars per lb",
            "env": ["MARS_API_KEY"],
            "requires": ["food_dairy"],
        },
        "SEFJ04": {
            "name": "Other dairy and related products",
            "tier": 1,
            "primary": "USDA NDPSR + federal milk order announcements",
            "secondary": [],
            "unit": "dollars per lb / dollars per cwt",
            "env": ["MARS_API_KEY"],
            "requires": ["food_dairy"],
        },
        "SEFS01": {
            "name": "Butter and margarine",
            "tier": 1,
            "primary": "USDA NDPSR butter price",
            "secondary": [],
            "unit": "dollars per lb",
            "env": ["MARS_API_KEY"],
            "requires": ["food_dairy"],
        },
    }
)


def load_env() -> None:
    for path in [WORKSPACE / ".env", ROOT / ".env"]:
        if not path.exists():
            continue
        for raw in path.read_text(encoding="utf-8-sig").splitlines():
            if not raw or raw.lstrip().startswith("#") or "=" not in raw:
                continue
            key, value = raw.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


def _redact(text: str | None) -> str | None:
    if text is None:
        return None
    out = text
    for name in ["EIA_API_KEY", "FRED_API_KEY", "MARS_API_KEY", "BLS_API_KEY"]:
        value = os.environ.get(name)
        if value:
            out = out.replace(value, "***")
    out = re.sub(r"(api_key=)[^&\s]+", r"\1***", out)
    return out


def _fetch_text(url: str, *, timeout: int = 20) -> tuple[str | None, str | None]:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=timeout) as response:
            return response.read().decode("utf-8", errors="replace"), None
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:500]
        return None, _redact(f"HTTP {exc.code}: {body}")
    except URLError as exc:
        return None, _redact(f"URL error: {exc.reason}")
    except OSError as exc:
        return None, _redact(f"OS error: {exc}")
    except TimeoutError:
        return None, "timeout"


def _fetch_bytes(url: str, *, timeout: int = 30, headers: dict[str, str] | None = None) -> tuple[bytes | None, str | None]:
    request_headers = {"User-Agent": USER_AGENT}
    request_headers.update(headers or {})
    request = Request(url, headers=request_headers)
    try:
        with urlopen(request, timeout=timeout) as response:
            return response.read(), None
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:500]
        return None, _redact(f"HTTP {exc.code}: {body}")
    except URLError as exc:
        return None, _redact(f"URL error: {exc.reason}")
    except OSError as exc:
        return None, _redact(f"OS error: {exc}")
    except TimeoutError:
        return None, "timeout"


def _get_json(base_url: str, params: dict[str, Any], *, timeout: int = 30) -> dict[str, Any]:
    url = f"{base_url}?{urlencode(params, doseq=True)}"
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _status_error(feed: str, status: str, detail: str, unit: str) -> dict[str, Any]:
    return {
        "feed": feed,
        "status": status,
        "lastObservationDate": None,
        "latestValue": None,
        "unit": unit,
        "observations": [],
        "error": _redact(detail),
    }


def _load_pdf_text(url: str, *, write_path: Path | None = None) -> tuple[str | None, str | None, bytes | None]:
    raw, error = _fetch_bytes(url)
    if not raw:
        return None, error, None
    try:
        try:
            from pypdf import PdfReader
        except ModuleNotFoundError:
            if BUNDLED_SITE_PACKAGES.exists():
                sys.path.insert(0, str(BUNDLED_SITE_PACKAGES))
            from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(raw))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        if write_path:
            write_path.parent.mkdir(parents=True, exist_ok=True)
            write_path.write_bytes(raw)
            write_path.with_suffix(".txt").write_text(text, encoding="utf-8")
        return text, None, raw
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}", raw


def _parse_report_date(text: str, fallback: str | None = None) -> str:
    patterns = [
        r"Report for:\s*(?:\d{1,2}/\d{1,2}/\d{4}\s*(?:-|to)\s*)?(\d{1,2}/\d{1,2}/\d{4})",
        r"Report For:\s*(?:\d{1,2}/\d{1,2}/\d{4}\s*(?:-|to)\s*)?(\d{1,2}/\d{1,2}/\d{4})",
        r"(\d{1,2}/\d{1,2}/\d{4})",
        r"([A-Z][a-z]{2}\s+[A-Z][a-z]{2}\s+\d{1,2},\s+\d{4})",
        r"([A-Z][a-z]+\s+\d{1,2},\s+\d{4})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if not match:
            continue
        value = match.group(1)
        for fmt in ["%m/%d/%Y", "%a %b %d, %Y", "%B %d, %Y"]:
            try:
                return datetime.strptime(value, fmt).date().isoformat()
            except ValueError:
                pass
    return fallback or datetime.now(timezone.utc).date().isoformat()


def _first_float(pattern: str, text: str, *, flags: int = re.DOTALL, divide: float = 1.0) -> float | None:
    match = re.search(pattern, text, flags)
    if not match:
        return None
    return float(match.group(1).replace(",", "")) / divide


def _parse_month_start(text: str, pattern: str) -> str | None:
    match = re.search(pattern, text, re.IGNORECASE)
    if not match:
        return None
    try:
        return datetime.strptime(match.group(1), "%B %Y").date().replace(day=1).isoformat()
    except ValueError:
        return None


def _feed_from_observations(
    *,
    feed: str,
    status: str,
    unit: str,
    observations: list[dict[str, Any]],
    error: str | None = None,
    points: list[dict[str, Any]] | None = None,
    component_observations: dict[str, list[dict[str, Any]]] | None = None,
    resolution_table: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    latest = max(observations, key=lambda item: item["date"]) if observations else None
    payload = {
        "feed": feed,
        "status": status,
        "lastObservationDate": latest["date"] if latest else None,
        "latestValue": latest["value"] if latest else None,
        "unit": unit,
        "observations": observations,
        "points": points or [],
        "error": _redact(error),
    }
    if component_observations:
        payload["componentObservations"] = component_observations
    if resolution_table:
        payload["resolutionTable"] = resolution_table
    return payload


def _check_gaps(periods: list[str], max_gap_days: int) -> str | None:
    dates: list[datetime] = []
    for period in periods:
        try:
            dates.append(datetime.fromisoformat(period[:10]))
        except ValueError:
            continue
    dates = sorted(set(dates))
    if len(dates) < 2:
        return None
    for prior, current in zip(dates, dates[1:]):
        if (current - prior).days > max_gap_days:
            return f"gap greater than {max_gap_days} days between {prior.date()} and {current.date()}"
    return None


def _series_points(rows: list[dict[str, Any]], key: str = "value") -> list[dict[str, Any]]:
    points = []
    for row in rows:
        raw_value = row.get(key)
        if raw_value in {None, ""}:
            continue
        try:
            value = float(raw_value)
        except (TypeError, ValueError):
            continue
        points.append({"date": str(row["period"]), "value": value})
    return sorted(points, key=lambda item: item["date"])


def _pct_change_points(points: list[dict[str, Any]]) -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []
    ordered = sorted(points, key=lambda item: item["date"])
    for prior, current in zip(ordered, ordered[1:]):
        if prior["value"] in {None, 0} or current["value"] is None:
            continue
        changes.append({"date": current["date"], "value": float(current["value"]) / float(prior["value"]) - 1.0})
    return changes


def _quarter_to_month(quarter: str) -> str | None:
    match = re.match(r"(\d{4})q([1-4])", str(quarter).lower())
    if not match:
        return None
    quarter_month = {"1": "03", "2": "06", "3": "09", "4": "12"}[match.group(2)]
    return f"{match.group(1)}-{quarter_month}"


def fetch_eia_series(name: str, *, write_snapshots: bool = False) -> dict[str, Any]:
    load_env()
    spec = EIA_SERIES[name]
    if not os.environ.get("EIA_API_KEY"):
        return _status_error(spec["label"], "blocked_missing_key", "Set EIA_API_KEY to enable EIA pulls.", spec["unit"])
    params = {
        "api_key": os.environ["EIA_API_KEY"],
        "frequency": spec["frequency"],
        "data[0]": spec["data"],
        "facets[series][]": spec["series"],
        "sort[0][column]": "period",
        "sort[0][direction]": "desc",
        "offset": 0,
        "length": 5000,
    }
    try:
        payload = _get_json(f"{EIA_API}/{spec['route']}/data/", params)
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:500]
        return _status_error(spec["label"], "rejected", f"HTTP {exc.code}: {body}", spec["unit"])
    except Exception as exc:
        return _status_error(spec["label"], "unavailable", f"{type(exc).__name__}: {exc}", spec["unit"])
    rows = payload.get("response", {}).get("data", [])
    points = _series_points(rows, spec["data"])
    if not points:
        return _status_error(spec["label"], "unavailable", "EIA returned no observations.", spec["unit"])
    bad = [point for point in points[-500:] if not (spec["min"] <= point["value"] <= spec["max"])]
    if bad:
        return _status_error(spec["label"], "failed_sanity", "EIA values outside expected unit bounds.", spec["unit"])
    gap = _check_gaps([point["date"] for point in points[-36:]], 14 if spec["frequency"] == "weekly" else 7)
    if gap:
        return _status_error(spec["label"], "failed_sanity", gap, spec["unit"])
    if write_snapshots:
        path = FEED_CACHE_DIR / "eia" / f"{name}.json"
        write_json(path, {"series": name, "label": spec["label"], "unit": spec["unit"], "points": points})
    latest = points[-1]
    return {
        "feed": spec["label"],
        "status": "live",
        "lastObservationDate": latest["date"],
        "latestValue": latest["value"],
        "unit": spec["unit"],
        "observations": [{"date": latest["date"], "value": latest["value"], "label": spec["label"]}],
        "points": points,
        "error": None,
    }


def fetch_eia_electricity(*, write_snapshots: bool = False) -> dict[str, Any]:
    load_env()
    if not os.environ.get("EIA_API_KEY"):
        return _status_error("EIA residential retail electricity", "blocked_missing_key", "Set EIA_API_KEY to enable EIA pulls.", "cents per kWh")
    params = {
        "api_key": os.environ["EIA_API_KEY"],
        "frequency": "monthly",
        "data[0]": "price",
        "facets[stateid][]": "US",
        "facets[sectorid][]": "RES",
        "sort[0][column]": "period",
        "sort[0][direction]": "desc",
        "offset": 0,
        "length": 500,
    }
    try:
        payload = _get_json(f"{EIA_API}/electricity/retail-sales/data/", params)
    except Exception as exc:
        return _status_error("EIA residential retail electricity", "unavailable", f"{type(exc).__name__}: {exc}", "cents per kWh")
    points = _series_points(payload.get("response", {}).get("data", []), "price")
    if not points:
        return _status_error("EIA residential retail electricity", "unavailable", "EIA returned no observations.", "cents per kWh")
    if any(point["value"] <= 0 or point["value"] > 80 for point in points):
        return _status_error("EIA residential retail electricity", "failed_sanity", "Electricity price outside expected cents/kWh bounds.", "cents per kWh")
    if write_snapshots:
        write_json(FEED_CACHE_DIR / "eia" / "electricity_residential.json", {"series": "electricity_residential", "points": points})
    latest = points[-1]
    return {
        "feed": "EIA residential retail electricity",
        "status": "live",
        "lastObservationDate": latest["date"],
        "latestValue": latest["value"],
        "unit": "cents per kWh",
        "observations": [{"date": latest["date"], "value": latest["value"], "label": "EIA residential retail electricity"}],
        "points": points,
        "error": None,
    }


def fetch_fred(*, write_snapshots: bool = False) -> dict[str, Any]:
    load_env()
    if not os.environ.get("FRED_API_KEY"):
        return _status_error("FRED mirror layer", "blocked_missing_key", "Set FRED_API_KEY to enable FRED pulls.", "various")
    observations = []
    points_by_series: dict[str, list[dict[str, Any]]] = {}
    try:
        for series_id, label in FRED_SERIES.items():
            payload = _get_json(
                FRED_API,
                {
                    "api_key": os.environ["FRED_API_KEY"],
                    "file_type": "json",
                    "series_id": series_id,
                    "sort_order": "desc",
                    "limit": 5000,
                },
            )
            points = []
            for row in payload.get("observations", []):
                if row.get("value") in {None, "."}:
                    continue
                points.append({"date": row["date"], "value": float(row["value"])})
            points = sorted(points, key=lambda item: item["date"])
            if points:
                points_by_series[series_id] = points
                latest = points[-1]
                observations.append({"date": latest["date"], "value": latest["value"], "label": f"FRED {label}"})
    except Exception as exc:
        return _status_error("FRED mirror layer", "unavailable", f"{type(exc).__name__}: {exc}", "various")
    if not observations:
        return _status_error("FRED mirror layer", "unavailable", "FRED returned no observations.", "various")
    if write_snapshots:
        write_json(FEED_CACHE_DIR / "fred" / "mirror.json", {"series": points_by_series})
    latest_obs = max(observations, key=lambda item: item["date"])
    return {
        "feed": "FRED mirror layer",
        "status": "live",
        "lastObservationDate": latest_obs["date"],
        "latestValue": latest_obs["value"],
        "unit": "various",
        "observations": observations,
        "points": points_by_series,
        "error": None,
    }


def aaa_gas_snapshot(inputs_dir: Path | None = None) -> dict[str, Any]:
    url = "https://gasprices.aaa.com/"
    html, error = _fetch_text(url)
    snapshot: dict[str, Any] = {
        "feed": "AAA daily national average gasoline",
        "url": url,
        "status": "unavailable",
        "lastObservationDate": None,
        "latestValue": None,
        "unit": "dollars per gallon",
        "observations": [],
        "error": error,
    }
    if html:
        if inputs_dir:
            inputs_dir.mkdir(parents=True, exist_ok=True)
            (inputs_dir / "aaa_gasprices_raw.html").write_text(html, encoding="utf-8")
        match = re.search(r"Today.{1,4}s AAA National Average\s*\$([0-9]\.[0-9]{2,4})", html, re.IGNORECASE)
        if not match:
            match = re.search(r"<th>\s*Regular\s*</th>.*?<td>\s*\$([0-9]\.[0-9]{2,4})\s*</td>", html, re.IGNORECASE | re.DOTALL)
        if match:
            value = float(match.group(1))
            if not 1.0 <= value <= 8.0:
                return snapshot
            today = datetime.now(timezone.utc).date().isoformat()
            observation = {"date": today, "value": value, "label": "AAA current national regular"}
            snapshot.update(
                {
                    "status": "live_current_snapshot",
                    "lastObservationDate": today,
                    "latestValue": value,
                    "observations": [observation],
                    "error": None,
                }
            )
            AAA_ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
            archive_path = AAA_ARCHIVE_DIR / "daily_regular.csv"
            existing_dates = set()
            if archive_path.exists():
                with archive_path.open("r", newline="", encoding="utf-8") as handle:
                    existing_dates = {row["date"] for row in csv.DictReader(handle)}
            if today not in existing_dates:
                with archive_path.open("a", newline="", encoding="utf-8") as handle:
                    writer = csv.DictWriter(handle, fieldnames=["date", "value"])
                    if archive_path.stat().st_size == 0:
                        writer.writeheader()
                    writer.writerow({"date": today, "value": value})
    return snapshot


def fetch_zori(*, write_snapshots: bool = False) -> dict[str, Any]:
    candidates = [
        "https://files.zillowstatic.com/research/public_csvs/zori/Metro_zori_uc_sfrcondomfr_sm_month.csv",
        "https://files.zillowstatic.com/research/public_csvs/zori/Metro_zori_sm_month.csv",
        "https://files.zillowstatic.com/research/public_csvs/zori/Metro_zori_uc_sfr_sm_month.csv",
    ]
    errors = []
    for url in candidates:
        try:
            df = pd.read_csv(url)
            date_cols = [col for col in df.columns if re.match(r"20\d{2}-\d{2}-\d{2}", str(col))]
            if not date_cols:
                errors.append(f"{url}: no date columns")
                continue
            national = df[df.astype(str).apply(lambda row: row.str.contains("United States", case=False, regex=False).any(), axis=1)]
            row = national.iloc[0] if not national.empty else df.iloc[0]
            series = [{"date": col[:7], "value": float(row[col])} for col in date_cols if pd.notna(row[col])]
            if not series:
                errors.append(f"{url}: no series values")
                continue
            if write_snapshots:
                path = FEED_CACHE_DIR / "zillow" / "zori.csv"
                path.parent.mkdir(parents=True, exist_ok=True)
                df.to_csv(path, index=False)
            latest = series[-1]
            return {
                "feed": "Zillow ZORI",
                "status": "live",
                "lastObservationDate": latest["date"],
                "latestValue": latest["value"],
                "unit": "rent index",
                "observations": [{"date": latest["date"], "value": latest["value"], "label": "Zillow ZORI"}],
                "points": series,
                "error": None,
            }
        except Exception as exc:
            errors.append(f"{url}: {type(exc).__name__}")
    return _status_error("Zillow ZORI", "unavailable", "; ".join(errors[-3:]), "rent index")


def fetch_apartment_list(*, write_snapshots: bool = False) -> dict[str, Any]:
    page = "https://www.apartmentlist.com/research/category/data-rent-estimates"
    html, error = _fetch_text(page)
    if not html:
        return _status_error("Apartment List rent estimates", "unavailable", error or "page unavailable", "rent")
    matches = re.findall(r'"url":"(//assets\.ctfassets\.net/[^"]+Apartment_List_Rent_Estimates_[^"]+\.csv)"', html)
    if not matches:
        return _status_error("Apartment List rent estimates", "unavailable", "No rent-estimates CSV link found on public page.", "rent")
    history_match = next((match for match in matches if "_Summary_" not in match), matches[0])
    url = "https:" + history_match
    try:
        df = pd.read_csv(url)
    except Exception as exc:
        return _status_error("Apartment List rent estimates", "unavailable", f"{type(exc).__name__}: {exc}", "rent")
    if write_snapshots:
        path = FEED_CACHE_DIR / "apartment_list" / "rent_estimates.csv"
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)
    national = df[df.astype(str).apply(lambda row: row.str.contains("United States", case=False, regex=False).any(), axis=1)]
    if "bed_size" in df.columns:
        national = national[national["bed_size"].astype(str).str.lower().eq("overall")]
    row = national.iloc[0] if not national.empty else df.iloc[0]
    date_cols = [col for col in df.columns if re.match(r"20\d{2}_\d{2}$", str(col))]
    series = []
    for col in date_cols:
        if pd.isna(row[col]):
            continue
        series.append({"date": str(col).replace("_", "-"), "value": float(row[col])})
    if series:
        latest = series[-1]
        value = latest["value"]
        latest_date = latest["date"]
    else:
        value = float(row["price_overall"]) if "price_overall" in df.columns else None
        latest_date = datetime.now(timezone.utc).date().isoformat()
    latest_label = str(row.get("location_name") or row.get("Location") or row.get("name") or "Apartment List latest")
    if value is None or value <= 0:
        return _status_error("Apartment List rent estimates", "failed_sanity", "No positive numeric rent estimate found.", "rent")
    return {
        "feed": "Apartment List rent estimates",
        "status": "live",
        "lastObservationDate": latest_date,
        "latestValue": value,
        "unit": "rent",
        "observations": [{"date": latest_date, "value": value, "label": latest_label}],
        "points": series,
        "error": None,
    }


def fetch_ntri(*, write_snapshots: bool = False) -> dict[str, Any]:
    url = "https://www.bls.gov/cpi/research-series/r-cpi-ntr-and-r-cpi-atr.xlsx"
    try:
        request = Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,*/*",
            },
        )
        raw = urlopen(request, timeout=30).read()
        xlsx_path = FEED_CACHE_DIR / "bls" / "r-cpi-ntr-and-r-cpi-atr.xlsx"
        xlsx_path.parent.mkdir(parents=True, exist_ok=True)
        xlsx_path.write_bytes(raw)
        df = pd.read_excel(xlsx_path, sheet_name="R-CPI-NTR", header=1)
    except Exception as exc:
        return _status_error("BLS New Tenant Rent Index", "unavailable", f"{type(exc).__name__}: {exc}", "index")
    if write_snapshots:
        path = FEED_CACHE_DIR / "bls" / "ntri.csv"
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)
    df = df.rename(columns={df.columns[0]: "quarter"})
    ntri_col = next((col for col in df.columns if str(col).strip() == "R-CPI-NTR"), None)
    if not ntri_col:
        return _status_error("BLS New Tenant Rent Index", "failed_sanity", "No numeric NTRI columns found.", "index")
    clean = df[pd.to_numeric(df[ntri_col], errors="coerce").notna()].copy()
    clean[ntri_col] = pd.to_numeric(clean[ntri_col], errors="coerce")
    points = []
    for _, row in clean.iterrows():
        month = _quarter_to_month(str(row["quarter"]))
        if month:
            points.append({"date": month, "value": float(row[ntri_col])})
    value = float(clean[ntri_col].iloc[-1])
    quarter = str(clean["quarter"].iloc[-1])
    return {
        "feed": "BLS New Tenant Rent Index",
        "status": "live",
        "lastObservationDate": quarter,
        "latestValue": value,
        "unit": "index",
        "observations": [{"date": quarter, "value": value, "label": "BLS NTRI latest"}],
        "points": points,
        "error": None,
    }


def _candidate_manheim_urls() -> list[str]:
    today = datetime.now(timezone.utc).date()
    candidates: list[str] = []
    for offset in range(1, 5):
        month_index = today.year * 12 + today.month - 1 - offset
        year = month_index // 12
        month = month_index % 12 + 1
        label = datetime(year, month, 1).strftime("%B-%Y")
        upload_index = year * 12 + month
        upload_year = upload_index // 12
        upload_month = upload_index % 12 + 1
        candidates.append(
            f"https://www.coxautoinc.com/wp-content/uploads/{upload_year}/{upload_month:02d}/"
            f"{label}-Manheim-Used-Vehicle-Value-Index.xlsx"
        )
    candidates.extend(
        [
            "https://www.coxautoinc.com/wp-content/uploads/2026/06/May-2026-Manheim-Used-Vehicle-Value-Index.xlsx",
            "https://site.manheim.com/wp-content/uploads/sites/2/2023/09/Aug-2023-ManheimUsedVehicleValueIndex-web-table-data-.xlsx",
        ]
    )
    return list(dict.fromkeys(candidates))


def _parse_manheim_history(df: pd.DataFrame) -> pd.DataFrame:
    clean = df.copy()
    clean = clean.rename(columns={clean.columns[0]: "date"})
    clean["date"] = pd.to_datetime(clean["date"], errors="coerce")
    clean = clean.dropna(subset=["date"]).copy()
    clean["date"] = clean["date"].dt.to_period("M").dt.to_timestamp()
    idx_col = None
    for candidate in ("Index (1/97 = 100)", "index_sa", "index"):
        if candidate in clean.columns:
            idx_col = candidate
            break
    if idx_col is None:
        for column in clean.columns:
            if column == "date":
                continue
            numeric = pd.to_numeric(clean[column], errors="coerce")
            if numeric.between(50, 500).mean() > 0.8:
                idx_col = column
                break
    if idx_col is None:
        raise ValueError("No Manheim UVVI SA index column found.")
    out = pd.DataFrame({"date": clean["date"], "value": pd.to_numeric(clean[idx_col], errors="coerce")})
    out = out.dropna(subset=["value"]).drop_duplicates("date").sort_values("date").reset_index(drop=True)
    if out.empty:
        raise ValueError("No numeric UVVI values found.")
    if not out["value"].between(50, 400).all():
        raise ValueError("UVVI outside expected index bounds.")
    return out


def fetch_manheim(*, write_snapshots: bool = False) -> dict[str, Any]:
    manual = DATA_DIR / "manual" / "manheim_uvvi.csv"
    try:
        if manual.exists():
            df = pd.read_csv(manual)
            source = str(manual)
        else:
            errors = []
            df = None
            source = ""
            for url in _candidate_manheim_urls():
                try:
                    df = pd.read_excel(url, sheet_name="DATA")
                    source = url
                    break
                except Exception as exc:
                    errors.append(f"{url}: {type(exc).__name__}")
            if df is None:
                return _status_error("Manheim UVVI", "unavailable", "; ".join(errors[-3:]), "index")
        if write_snapshots:
            path = FEED_CACHE_DIR / "manheim" / "uvvi.csv"
            path.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(path, index=False)
        history = _parse_manheim_history(df)
        value = float(history["value"].iloc[-1])
        last_month = history["date"].iloc[-1].strftime("%Y-%m")
        publication_date = manheim_final_publication_date(last_month).isoformat()
        points = [
            {"date": row["date"].strftime("%Y-%m"), "value": float(row["value"])}
            for _, row in history.iterrows()
        ]
        return {
            "feed": "Manheim UVVI",
            "status": "live",
            "lastObservationDate": last_month,
            "latestValue": value,
            "unit": "index",
            "observations": [{"date": last_month, "value": value, "label": "Manheim UVVI final"}],
            "points": points,
            "publicationDate": publication_date,
            "timingEnforced": True,
            "publicationRule": "month-end final assumed published on the 7th of the following month, weekend-adjusted; lag 0 is used only if publication date is before CPI release",
            "error": None if manual.exists() else f"Loaded public XLSX ({source}); add data/manual/manheim_uvvi.csv to override.",
        }
    except Exception as exc:
        return _status_error("Manheim UVVI", "unavailable", f"{type(exc).__name__}: {exc}", "index")


def fetch_usda_beef_cutout(*, write_snapshots: bool = False) -> dict[str, Any]:
    url = f"{USDA_MNREPORTS}/ams_2453.pdf"
    path = FEED_CACHE_DIR / "usda" / "beef_boxed_cutout_pm.pdf" if write_snapshots else None
    text, error, _ = _load_pdf_text(url, write_path=path)
    if not text:
        return _status_error("USDA boxed beef cutout PM", "unavailable", error or "PDF unavailable", "dollars per cwt")
    date = _parse_report_date(text)
    match = re.search(r"Current Cutout Values:\s*([\d,.]+)\s+([\d,.]+)", text, re.DOTALL)
    if not match:
        return _status_error("USDA boxed beef cutout PM", "needs_parser_work", "Could not parse Current Cutout Values from USDA PDF.", "dollars per cwt")
    choice = float(match.group(1).replace(",", ""))
    select = float(match.group(2).replace(",", ""))
    if not (50 <= choice <= 800 and 50 <= select <= 800):
        return _status_error("USDA boxed beef cutout PM", "failed_sanity", "Boxed beef cutout outside expected $/cwt bounds.", "dollars per cwt")
    observations = [
        {"date": date, "value": choice, "label": "USDA boxed beef Choice cutout"},
        {"date": date, "value": select, "label": "USDA boxed beef Select cutout"},
    ]
    spread = _first_float(r"Choice/Select spread:\s*([\d,.]+)", text)
    if spread is not None:
        observations.append({"date": date, "value": spread, "label": "USDA boxed beef Choice/Select spread"})
    for primal in ["Rib", "Chuck", "Round", "Loin", "Brisket", "Short Plate", "Flank"]:
        primal_match = re.search(rf"Primal {re.escape(primal)}\s+([\d,.]+)\s+([\d,.]+)", text, re.DOTALL)
        if primal_match:
            observations.append({"date": date, "value": float(primal_match.group(1).replace(",", "")), "label": f"USDA boxed beef Choice primal {primal}"})
            observations.append({"date": date, "value": float(primal_match.group(2).replace(",", "")), "label": f"USDA boxed beef Select primal {primal}"})
    by_label = {obs["label"]: obs for obs in observations}
    beef_component_observations = {
        "SEFC": observations[:3],
        "SEFC01": [obs for label in ["USDA boxed beef Choice primal Chuck", "USDA boxed beef Choice primal Round", "USDA boxed beef Choice/Select spread"] if (obs := by_label.get(label))],
        "SEFC02": [obs for label in ["USDA boxed beef Choice primal Chuck", "USDA boxed beef Choice primal Round", "USDA boxed beef Choice/Select spread"] if (obs := by_label.get(label))],
        "SEFC03": [obs for label in ["USDA boxed beef Choice primal Loin", "USDA boxed beef Choice primal Rib", "USDA boxed beef Choice/Select spread"] if (obs := by_label.get(label))],
        "SEFC04": [obs for label in ["USDA boxed beef Choice cutout", "USDA boxed beef Choice/Select spread"] if (obs := by_label.get(label))],
    }
    return _feed_from_observations(
        feed="USDA boxed beef cutout PM",
        status="live_pdf_fallback",
        unit="dollars per cwt",
        observations=observations,
        error="USDA MARS API did not expose legacy LMR JSON for slug 2453; parsed official AMS PDF.",
        component_observations={key: value for key, value in beef_component_observations.items() if value},
    )


def fetch_usda_pork_cutout(*, write_snapshots: bool = False) -> dict[str, Any]:
    url = f"{USDA_MNREPORTS}/ams_2498.pdf"
    path = FEED_CACHE_DIR / "usda" / "pork_cutout_pm.pdf" if write_snapshots else None
    text, error, _ = _load_pdf_text(url, write_path=path)
    if not text:
        return _status_error("USDA pork cutout PM", "unavailable", error or "PDF unavailable", "dollars per cwt")
    row = re.search(
        r"(\d{1,2}/\d{1,2}/\d{4})\s+([\d,.]+)\s+([\d,.]+)\s+([\d,.]+)\s+([\d,.]+)\s+([\d,.]+)\s+([\d,.]+)\s+([\d,.]+)\s+([\d,.]+)",
        text,
        re.DOTALL,
    )
    if not row:
        return _status_error("USDA pork cutout PM", "needs_parser_work", "Could not parse primal cutout table from USDA PDF.", "dollars per cwt")
    date = datetime.strptime(row.group(1), "%m/%d/%Y").date().isoformat()
    labels = ["loads", "carcass", "loin", "butt", "picnic", "rib", "ham", "belly"]
    values = [float(row.group(index).replace(",", "")) for index in range(2, 10)]
    if not (20 <= values[1] <= 250):
        return _status_error("USDA pork cutout PM", "failed_sanity", "Pork carcass cutout outside expected $/cwt bounds.", "dollars per cwt")
    observations = [{"date": date, "value": values[1], "label": "USDA pork cutout carcass"}]
    observations.extend(
        {"date": date, "value": value, "label": f"USDA pork cutout {label}"}
        for label, value in zip(labels, values)
        if label != "carcass"
    )
    component_obs = [obs for obs in observations if "loads" not in obs["label"]]
    by_label = {obs["label"]: obs for obs in component_obs}
    pork_component_observations = {
        "SEFD": component_obs,
        "SEFD01": [obs for label in ["USDA pork cutout belly"] if (obs := by_label.get(label))],
        "SEFD02": [obs for label in ["USDA pork cutout ham"] if (obs := by_label.get(label))],
        "SEFD03": [obs for label in ["USDA pork cutout loin"] if (obs := by_label.get(label))],
        "SEFD04": [obs for label in ["USDA pork cutout carcass"] if (obs := by_label.get(label))],
    }
    return _feed_from_observations(
        feed="USDA pork cutout PM",
        status="live_pdf_fallback",
        unit="dollars per cwt",
        observations=observations,
        error="Parsed official AMS PDF because MARS legacy LMR JSON was not available through the current endpoint.",
        component_observations={key: value for key, value in pork_component_observations.items() if value},
    )


def fetch_usda_eggs(*, write_snapshots: bool = False) -> dict[str, Any]:
    url = f"{USDA_MNREPORTS}/ams_2848.pdf"
    path = FEED_CACHE_DIR / "usda" / "weekly_combined_shell_eggs.pdf" if write_snapshots else None
    text, error, _ = _load_pdf_text(url, write_path=path)
    if not text:
        return _status_error("USDA weekly combined shell eggs", "unavailable", error or "PDF unavailable", "cents per dozen")
    date = _parse_report_date(text)
    block = re.search(r"National Shell Eggs - Caged.*?(?=Midwest Shell Eggs|Page 1)", text, re.DOTALL)
    source = block.group(0) if block else text
    observations = []
    for size in ["Extra Large", "Large", "Medium"]:
        match = re.search(rf"\n{re.escape(size)}\s+([\d,.]+)\s*-\s*([\d,.]+)\s+([\d,.]+)", source, re.DOTALL)
        if match:
            low = float(match.group(1).replace(",", ""))
            high = float(match.group(2).replace(",", ""))
            average = float(match.group(3).replace(",", ""))
            observations.append({"date": date, "value": average, "label": f"USDA combined regional caged white {size} eggs average"})
            observations.append({"date": date, "value": (low + high) / 2, "label": f"USDA combined regional caged white {size} eggs midpoint"})
    if not observations:
        return _status_error("USDA weekly combined shell eggs", "needs_parser_work", "Could not parse national caged white egg prices from USDA PDF.", "cents per dozen")
    if any(obs["value"] <= 0 or obs["value"] > 800 for obs in observations):
        return _status_error("USDA weekly combined shell eggs", "failed_sanity", "Egg price outside expected cents/dozen bounds.", "cents per dozen")
    return _feed_from_observations(
        feed="USDA weekly combined shell eggs",
        status="live_pdf_fallback",
        unit="cents per dozen",
        observations=observations,
        error="Parsed official AMS PDF; MARS JSON returned report headers only for this report.",
        component_observations={"SEFH": observations},
    )


def fetch_usda_chicken(*, write_snapshots: bool = False) -> dict[str, Any]:
    url = f"{USDA_MNREPORTS}/ams_3646.pdf"
    path = FEED_CACHE_DIR / "usda" / "weekly_national_chicken.pdf" if write_snapshots else None
    text, error, _ = _load_pdf_text(url, write_path=path)
    if not text:
        return _status_error("USDA weekly national chicken", "unavailable", error or "PDF unavailable", "cents per lb")
    date = _parse_report_date(text)
    specs = [
        ("National composite whole bird", r"National Composite Whole\s*Bird:\s*([\d,.]+)\s*-\s*[\d,.]+\s+([\d,.]+)"),
        ("National composite WOGS", r"National Composite WOGS:\s*([\d,.]+)\s*-\s*[\d,.]+\s+([\d,.]+)"),
        ("Boneless skinless breast", r"Breast - B/S:\s*([\d,.]+)\s*-\s*[\d,.]+\s+([\d,.]+)"),
        ("Leg quarters bulk", r"Leg quarters - Bulk:\s*([\d,.]+)\s*-\s*[\d,.]+\s+([\d,.]+)"),
        ("Whole wings", r"Wings - Whole:\s*([\d,.]+)\s*-\s*[\d,.]+\s+([\d,.]+)"),
    ]
    observations = []
    for label, pattern in specs:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            observations.append({"date": date, "value": float(match.group(2).replace(",", "")), "label": f"USDA chicken {label}"})
    if not observations:
        return _status_error("USDA weekly national chicken", "needs_parser_work", "Could not parse chicken composite prices from USDA PDF.", "cents per lb")
    if any(obs["value"] <= 0 or obs["value"] > 600 for obs in observations):
        return _status_error("USDA weekly national chicken", "failed_sanity", "Chicken price outside expected cents/lb bounds.", "cents per lb")
    by_label = {obs["label"]: obs for obs in observations}
    parts = [obs for label in ["USDA chicken Boneless skinless breast", "USDA chicken Leg quarters bulk", "USDA chicken Whole wings"] if (obs := by_label.get(label))]
    chicken_component_observations = {
        "SEFF": observations,
        "SEFF01": observations,
        "SEFF02": parts,
    }
    return _feed_from_observations(
        feed="USDA weekly national chicken",
        status="live_pdf_fallback",
        unit="cents per lb",
        observations=observations,
        error="Parsed official AMS PDF; feed-cost and HPAI shock features remain separate.",
        component_observations={key: value for key, value in chicken_component_observations.items() if value},
    )


def fetch_usda_dairy(*, write_snapshots: bool = False) -> dict[str, Any]:
    ndpsr_url = f"{USDA_MNREPORTS}/dywdairyproductssales.pdf"
    advanced_url = f"{USDA_MNREPORTS}/dymadvancedprices.pdf"
    class_url = f"{USDA_MNREPORTS}/dymclassprices.pdf"
    ndpsr_text, ndpsr_error, _ = _load_pdf_text(ndpsr_url, write_path=FEED_CACHE_DIR / "usda" / "ndpsr.pdf" if write_snapshots else None)
    advanced_text, advanced_error, _ = _load_pdf_text(advanced_url, write_path=FEED_CACHE_DIR / "usda" / "advanced_milk_prices.pdf" if write_snapshots else None)
    class_text, class_error, _ = _load_pdf_text(class_url, write_path=FEED_CACHE_DIR / "usda" / "class_component_milk_prices.pdf" if write_snapshots else None)
    observations: list[dict[str, Any]] = []
    component: dict[str, list[dict[str, Any]]] = {"SEFJ": [], "SEFJ01": [], "SEFJ02": [], "SEFJ03": [], "SEFJ04": [], "SEFS01": []}
    if ndpsr_text:
        named_dates = re.findall(r"week ending\s+([A-Z][a-z]+\s+\d{1,2},\s+\d{4})", ndpsr_text)
        date = datetime.strptime(named_dates[-1], "%B %d, %Y").date().isoformat() if named_dates else _parse_report_date(ndpsr_text)
        specs = [
            ("Butter", r"Butter prices.*?averaged\s+\$([\d,.]+)", 1.0, "SEFS01"),
            ("Cheddar 40-pound blocks", r"Cheddar Cheese prices.*?averaged\s+\$([\d,.]+)", 1.0, "SEFJ02"),
            ("Dry whey", r"Dry Whey prices.*?averaged\s+([\d,.]+)\s+cents", 100.0, "SEFJ03"),
            ("Nonfat dry milk", r"Nonfat Dry Milk prices.*?averaged\s+\$([\d,.]+)", 1.0, "SEFJ03"),
        ]
        for label, pattern, divide, code in specs:
            value = _first_float(pattern, ndpsr_text, divide=divide)
            if value is not None:
                obs = {"date": date, "value": value, "label": f"USDA NDPSR {label}"}
                observations.append(obs)
                component.setdefault(code, []).append(obs)
                if code != "SEFJ":
                    component["SEFJ"].append(obs)
                if code == "SEFJ03":
                    component["SEFJ04"].append(obs)
    if advanced_text:
        date = _parse_month_start(advanced_text, r"Announcement of Advanced Prices and Pricing Factors for\s+([A-Z][a-z]+\s+\d{4})") or _parse_report_date(advanced_text)
        class_i = _first_float(r"Base Class I Price:\s*\$([\d,.]+)", advanced_text)
        if class_i is not None:
            obs = {"date": date, "value": class_i, "label": "USDA advanced Base Class I milk price"}
            observations.append(obs)
            component.setdefault("SEFJ01", []).append(obs)
            component["SEFJ"].append(obs)
    if class_text:
        date = _parse_month_start(class_text, r"Announcement of Class and Component Prices for\s+([A-Z][a-z]+\s+\d{4})") or _parse_report_date(class_text)
        for label, pattern in [
            ("Class III milk price", r"Class III Price:\s*\$([\d,.]+)"),
            ("Class IV milk price", r"Class IV Price:\s*\$([\d,.]+)"),
        ]:
            value = _first_float(pattern, class_text)
            if value is not None:
                obs = {"date": date, "value": value, "label": f"USDA {label}"}
                observations.append(obs)
                component["SEFJ"].append(obs)
                component["SEFJ04"].append(obs)
    if not observations:
        return _status_error("USDA dairy product and milk-order prices", "unavailable", "; ".join(filter(None, [ndpsr_error, advanced_error, class_error])), "dollars")
    if any(obs["value"] <= 0 or obs["value"] > 100 for obs in observations):
        return _status_error("USDA dairy product and milk-order prices", "failed_sanity", "Dairy value outside expected bounds.", "dollars")
    return _feed_from_observations(
        feed="USDA dairy product and milk-order prices",
        status="live_pdf_fallback",
        unit="dollars per lb / dollars per cwt",
        observations=observations,
        error="Parsed official AMS dairy PDFs.",
        component_observations={key: value for key, value in component.items() if value},
    )


def _bls_tsv(path: str) -> tuple[pd.DataFrame | None, str | None]:
    text, error = _fetch_text(f"{BLS_TIME_SERIES}/{path}", timeout=30)
    if not text:
        return None, error
    df = pd.read_csv(io.StringIO(text), sep="\t")
    df.columns = [str(col).strip() for col in df.columns]
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()
    return df, None


def fetch_bls_food_average_prices(*, write_snapshots: bool = False) -> dict[str, Any]:
    load_env()
    if not os.environ.get("BLS_API_KEY"):
        return _status_error("BLS food average-price validators", "blocked_missing_key", "Set BLS_API_KEY to enable BLS food AP pulls.", "retail price")
    items, item_error = _bls_tsv("ap/ap.item")
    series, series_error = _bls_tsv("ap/ap.series")
    data, data_error = _bls_tsv("ap/ap.data.0.Current")
    if items is None or series is None or data is None:
        return _status_error("BLS food average-price validators", "unavailable", "; ".join(filter(None, [item_error, series_error, data_error])), "retail price")
    data.columns = [str(col).strip() for col in data.columns]
    series.columns = [str(col).strip() for col in series.columns]
    validators = [
        {"name": "eggs", "terms": ["Eggs, grade A, large"], "codes": ["SEFH"]},
        {"name": "milk", "terms": ["Milk, fresh, whole, fortified, per gal"], "codes": ["SEFJ", "SEFJ01"]},
        {"name": "bread", "terms": ["Bread, white, pan"], "codes": ["SEFB01", "SAF111"]},
        {"name": "ground beef", "terms": ["Ground beef, 100% beef"], "codes": ["SEFC", "SEFC01"]},
        {"name": "bacon", "terms": ["Bacon, sliced"], "codes": ["SEFD", "SEFD01"]},
        {"name": "chicken", "terms": ["Chicken, fresh, whole"], "codes": ["SEFF", "SEFF01"]},
        {"name": "bananas", "terms": ["Bananas"], "codes": ["SEFK"]},
        {"name": "tomatoes", "terms": ["Tomatoes, field grown"], "codes": ["SEFL"]},
        {"name": "potatoes", "terms": ["Potatoes, white, per lb", "Potatoes, white"], "codes": ["SEFL"]},
        {"name": "coffee", "terms": ["Coffee, 100%, ground roast, all sizes"], "codes": ["SEFP01"]},
    ]
    observations: list[dict[str, Any]] = []
    component: dict[str, list[dict[str, Any]]] = {}
    resolution: list[dict[str, Any]] = []
    errors: list[str] = []
    for validator in validators:
        item_row = None
        for term in validator["terms"]:
            matches = items[items["item_name"].str.contains(term, case=False, regex=False, na=False)]
            if not matches.empty:
                item_row = matches.iloc[0]
                break
        if item_row is None:
            errors.append(f"{validator['name']}: AP item not found")
            continue
        item_code = str(item_row["item_code"])
        series_rows = series[(series["item_code"].astype(str) == item_code) & (series["area_code"].astype(str) == "0000")]
        if series_rows.empty:
            errors.append(f"{validator['name']}: U.S. city average series not found")
            continue
        series_rows = series_rows.assign(sort_key=series_rows["end_year"].astype(str) + series_rows["end_period"].astype(str))
        series_id = str(series_rows.sort_values("sort_key").iloc[-1]["series_id"])
        rows = data[(data["series_id"].astype(str) == series_id) & data["period"].astype(str).str.startswith("M")].copy()
        rows["value"] = pd.to_numeric(rows["value"], errors="coerce")
        rows = rows.dropna(subset=["value"])
        if rows.empty:
            errors.append(f"{validator['name']}: no AP observations")
            continue
        rows["month"] = rows["year"].astype(str) + "-" + rows["period"].str[1:].str.zfill(2)
        latest = rows.sort_values("month").iloc[-1]
        obs = {"date": str(latest["month"]), "value": float(latest["value"]), "label": f"BLS AP {item_row['item_name']}"}
        observations.append(obs)
        resolution.append({"validator": validator["name"], "itemCode": item_code, "seriesId": series_id, "itemName": str(item_row["item_name"])})
        for code in validator["codes"]:
            component.setdefault(code, []).append(obs)
        if write_snapshots:
            path = FEED_CACHE_DIR / "bls" / f"ap_{validator['name'].replace(' ', '_')}.csv"
            path.parent.mkdir(parents=True, exist_ok=True)
            rows.to_csv(path, index=False)
    if write_snapshots:
        write_json(FEED_CACHE_DIR / "bls" / "food_ap_resolution.json", resolution)
    if not observations:
        return _status_error("BLS food average-price validators", "unavailable", "; ".join(errors), "retail price")
    return _feed_from_observations(
        feed="BLS food average-price validators",
        status="live" if not errors else "partial_live_fallback",
        unit="retail price",
        observations=observations,
        error="; ".join(errors) if errors else None,
        component_observations=component,
        resolution_table=resolution,
    )


def fetch_aphis_hpai(*, write_snapshots: bool = False) -> dict[str, Any]:
    url = "https://www.aphis.usda.gov/livestock-poultry-disease/avian/avian-influenza/hpai-detections/commercial-backyard-flocks"
    html, error = _fetch_text(url, timeout=30)
    if not html:
        return _status_error("APHIS HPAI detections", "unavailable", error or "APHIS page unavailable", "birds affected")
    if write_snapshots:
        path = FEED_CACHE_DIR / "aphis" / "hpai_page.html"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8")
    iframe = re.search(r'<iframe[^>]+src="([^"]+)"', html)
    detail = "Public APHIS page found; detections are embedded in a Tableau dashboard and need a workbook-data parser for layer/broiler bird counts."
    if iframe:
        detail += " Tableau dashboard source captured in cache."
    return _status_error("APHIS HPAI detections", "needs_parser_work", detail, "birds affected")


def fetch_usda_produce_basket(*, write_snapshots: bool = False) -> dict[str, Any]:
    load_env()
    if not os.environ.get("MARS_API_KEY"):
        return _status_error("USDA terminal-market produce basket", "blocked_missing_key", "Set MARS_API_KEY to enable produce terminal-market pulls.", "produce price")
    auth = base64.b64encode(f"{os.environ['MARS_API_KEY']}:".encode("utf-8")).decode("ascii")
    raw, error = _fetch_bytes(f"{USDA_MNREPORTS.replace('www.ams.usda.gov/mnreports', 'marsapi.ams.usda.gov/services/v1.2')}/reports", headers={"Authorization": f"Basic {auth}"}, timeout=30)
    if write_snapshots and raw:
        path = FEED_CACHE_DIR / "usda" / "mars_reports.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    if not raw:
        return _status_error("USDA terminal-market produce basket", "unavailable", error or "MARS report list unavailable", "produce price")
    return _status_error(
        "USDA terminal-market produce basket",
        "needs_parser_work",
        "MARS report list is reachable, but the CPI produce basket needs canonical item/city spec filters before ingesting terminal-market PDFs.",
        "produce price",
    )


def fetch_futures(*, write_snapshots: bool = False) -> dict[str, Any]:
    symbols = {"coffee": "KC=F", "sugar": "SB=F"}
    observations = []
    errors = []
    for label, symbol in symbols.items():
        now = int(datetime.now(timezone.utc).timestamp())
        start = now - 120 * 86_400
        url = f"https://query1.finance.yahoo.com/v7/finance/download/{symbol}?period1={start}&period2={now}&interval=1d&events=history&includeAdjustedClose=true"
        try:
            df = pd.read_csv(url)
            if df.empty or "Close" not in df.columns:
                errors.append(f"{label}: no close")
                continue
            latest = df.dropna(subset=["Close"]).iloc[-1]
            value = float(latest["Close"])
            if value <= 0:
                errors.append(f"{label}: nonpositive")
                continue
            observations.append({"date": str(latest["Date"]), "value": value, "label": f"ICE/Yahoo {label} futures"})
            if write_snapshots:
                path = FEED_CACHE_DIR / "futures" / f"{label.replace(' ', '_')}.csv"
                path.parent.mkdir(parents=True, exist_ok=True)
                df.to_csv(path, index=False)
        except Exception as exc:
            errors.append(f"{label}: {type(exc).__name__}")
    if not observations:
        return _status_error("ICE softs futures fallback", "unavailable", "; ".join(errors), "settlement")
    latest_obs = max(observations, key=lambda item: item["date"])
    return {
        "feed": "ICE softs futures fallback",
        "status": "live",
        "lastObservationDate": latest_obs["date"],
        "latestValue": latest_obs["value"],
        "unit": "settlement",
        "observations": observations,
        "points": [],
        "error": "; ".join(errors) if errors else None,
    }


def collect_feeds(*, write_snapshots: bool = False) -> dict[str, dict[str, Any]]:
    eia = {name: fetch_eia_series(name, write_snapshots=write_snapshots) for name in EIA_SERIES}
    eia["electricity_residential"] = fetch_eia_electricity(write_snapshots=write_snapshots)
    return {
        **eia,
        "cme_futures": collect_cme_futures(FEED_CACHE_DIR / "cme", write_snapshots=write_snapshots),
        "fred": fetch_fred(write_snapshots=write_snapshots),
        "aaa": aaa_gas_snapshot(),
        "zori": fetch_zori(write_snapshots=write_snapshots),
        "apartment_list": fetch_apartment_list(write_snapshots=write_snapshots),
        "ntri": fetch_ntri(write_snapshots=write_snapshots),
        "manheim": fetch_manheim(write_snapshots=write_snapshots),
        "futures": fetch_futures(write_snapshots=write_snapshots),
        "food_beef_cutout": fetch_usda_beef_cutout(write_snapshots=write_snapshots),
        "food_pork_cutout": fetch_usda_pork_cutout(write_snapshots=write_snapshots),
        "food_eggs": fetch_usda_eggs(write_snapshots=write_snapshots),
        "food_chicken": fetch_usda_chicken(write_snapshots=write_snapshots),
        "food_dairy": fetch_usda_dairy(write_snapshots=write_snapshots),
        "bls_food_ap": fetch_bls_food_average_prices(write_snapshots=write_snapshots),
        "hpai": fetch_aphis_hpai(write_snapshots=write_snapshots),
        "food_produce": fetch_usda_produce_basket(write_snapshots=write_snapshots),
    }


def monthly_average(points: list[dict[str, Any]], month: str) -> float | None:
    vals = [point["value"] for point in points if point["date"].startswith(month)]
    return sum(vals) / len(vals) if vals else None


def _mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def shelter_market_rent_signal(month: str, feeds: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    start = add_months(month, -18)
    end = add_months(month, -6)
    specs = [
        ("zori", "Zillow ZORI", 0.40),
        ("apartment_list", "Apartment List", 0.35),
        ("ntri", "BLS/Cleveland Fed NTRI", 0.25),
    ]
    pieces: list[dict[str, Any]] = []
    weighted = 0.0
    weight_sum = 0.0
    for key, label, weight in specs:
        feed = feeds.get(key, {})
        if feed.get("status") not in LIVE_STATUSES:
            continue
        changes = _pct_change_points(feed.get("points") or [])
        window = [point for point in changes if start <= point["date"] <= end]
        value = _mean([float(point["value"]) for point in window])
        if value is None:
            continue
        # Asking/new-tenant indexes are noisier than CPI shelter. Cap the overlay input,
        # then keep it small in the final shelter blend.
        value = min(max(value, -0.01), 0.01)
        pieces.append(
            {
                "feed": label,
                "windowStart": start,
                "windowEnd": end,
                "observations": len(window),
                "value": value,
                "weight": weight,
            }
        )
        weighted += weight * value
        weight_sum += weight
    if not pieces or weight_sum <= 0:
        return None
    signal = weighted / weight_sum
    driver = "; ".join(
        f"{piece['feed']} {piece['value'] * 100:.2f}% avg m/m over {piece['observations']} lagged obs"
        for piece in pieces
    )
    return {
        "value": signal,
        "driver": f"lagged external shelter overlay ({start} to {end}): {driver}",
        "pieces": pieces,
    }


def eia_gasoline_forecast_mm(month: str, feeds: dict[str, dict[str, Any]]) -> tuple[float | None, str | None]:
    candidates = [
        ("gasoline_regular", "EIA weekly regular gasoline", "weekly prints"),
        ("gasoline_all_grades", "EIA weekly all-grades gasoline", "weekly prints"),
        ("rbob", "EIA daily RBOB spot gasoline", "daily prints"),
    ]
    for key, label, count_label in candidates:
        gas = feeds.get(key, {})
        if gas.get("status") != "live":
            continue
        points = gas.get("points") or []
        current = monthly_average(points, month)
        prior = monthly_average(points, add_months(month, -1))
        if current is None or prior in {None, 0}:
            continue
        move = current / prior - 1.0
        values = [point for point in points if point["date"].startswith(month)]
        driver = (
            f"{label} calendar-month average ${current:.3f}/gal "
            f"vs prior ${prior:.3f}/gal using {len(values)} {count_label}"
        )
        return move, driver
    return None, None


def eia_jet_fuel_forecast_mm(month: str, feeds: dict[str, dict[str, Any]]) -> tuple[float | None, str | None]:
    jet = feeds.get("jet_fuel", {})
    if jet.get("status") != "live":
        return None, None
    points = jet.get("points") or []
    current = monthly_average(points, month)
    prior = monthly_average(points, add_months(month, -1))
    if current is None or prior in {None, 0}:
        return None, None
    move = current / prior - 1.0
    values = [point for point in points if point["date"].startswith(month)]
    driver = (
        f"EIA Gulf Coast jet fuel calendar-month average ${current:.3f}/gal "
        f"vs prior ${prior:.3f}/gal using {len(values)} daily prints"
    )
    return move, driver


def component_status(code: str, feed: dict[str, Any], feeds: dict[str, dict[str, Any]]) -> dict[str, Any]:
    if code == "SETE":
        return {
            "status": "licensed_only_fallback",
            "fallbackUsed": True,
            "lastObservationDate": None,
            "latestValue": None,
            "observationsUsed": [],
            "details": "No free national rate-filing feed exists; licensed tracker required.",
        }
    required = feed.get("requires", [])
    statuses = [feeds[item] for item in required if item in feeds]
    live = [item for item in statuses if item.get("status") in LIVE_STATUSES]
    observations = []
    for item in statuses:
        component_obs = (item.get("componentObservations") or {}).get(code)
        observations.extend(component_obs if component_obs is not None else item.get("observations", []))
    details = "; ".join(filter(None, [_redact(item.get("error")) for item in statuses]))
    if required and len(live) == len(required):
        status = "live"
        fallback = False
    elif live:
        status = "partial_live_fallback"
        fallback = True
    else:
        status = "fallback"
        fallback = True
    latest_obs = max(observations, key=lambda item: item["date"]) if observations else None
    return {
        "status": status,
        "fallbackUsed": fallback,
        "lastObservationDate": latest_obs["date"] if latest_obs else None,
        "latestValue": latest_obs["value"] if latest_obs else None,
        "observationsUsed": observations,
        "details": details or None,
    }


def build_feed_health(month: str, *, write_snapshots: bool = False) -> dict[str, Any]:
    run_dir = RUNS_DIR / month
    inputs_dir = run_dir / "inputs" if write_snapshots else None
    feeds = collect_feeds(write_snapshots=write_snapshots)
    shelter_signal = shelter_market_rent_signal(month, feeds)
    aaa = feeds["aaa"]
    if inputs_dir:
        inputs_dir.mkdir(parents=True, exist_ok=True)
        write_json(inputs_dir / "aaa_gas_snapshot.json", aaa)
    components = []
    for code, feed in TIER_FEEDS.items():
        status = component_status(code, feed, feeds)
        row = {
            "itemCode": code,
            "name": feed["name"],
            "tier": feed["tier"],
            "primaryFeed": feed["primary"],
            "secondaryFeeds": feed.get("secondary", []),
            "status": status["status"],
            "fallbackUsed": status["fallbackUsed"],
            "lastObservationDate": status["lastObservationDate"],
            "latestValue": status["latestValue"],
            "unit": feed["unit"],
            "observationsUsed": status["observationsUsed"],
            "details": _redact(status["details"]),
        }
        if code == "SETA02" and feeds.get("manheim"):
            manheim = feeds["manheim"]
            row["points"] = manheim.get("points") or []
            row["publicationDate"] = manheim.get("publicationDate")
            row["timingEnforced"] = manheim.get("timingEnforced", False)
            row["publicationRule"] = manheim.get("publicationRule")
        if code == "SETG01" and feeds.get("jet_fuel"):
            row["points"] = feeds["jet_fuel"].get("points") or []
        if code in {"SEHA", "SEHC", "SEHC01"} and shelter_signal:
            row["shelterMarketNsaMm"] = shelter_signal["value"]
            row["shelterMarketDriver"] = shelter_signal["driver"]
            row["shelterMarketPieces"] = shelter_signal["pieces"]
        components.append(row)
    live_count = sum(1 for row in components if row["status"] in LIVE_STATUSES)
    partial_count = sum(1 for row in components if row["status"].startswith("partial"))
    payload = {
        "forecastMonth": month,
        "generatedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "summary": {
            "componentsTracked": len(components),
            "live": live_count,
            "partial": partial_count,
            "fallbackOrBlocked": len(components) - live_count - partial_count,
        },
        "components": components,
        "cmeFutures": feeds.get("cme_futures", {}).get("products", []),
        "foodFuturesLagReport": food_futures_lag_report(feeds.get("cme_futures", {})),
    }
    gas_move, gas_driver = eia_gasoline_forecast_mm(month, feeds)
    jet_move, jet_driver = eia_jet_fuel_forecast_mm(month, feeds)
    payload["derived"] = {
        "gasolineEiaNsaMm": gas_move,
        "gasolineEiaDriver": gas_driver,
        "jetFuelEiaNsaMm": jet_move,
        "jetFuelEiaDriver": jet_driver,
        "shelterMarketNsaMm": shelter_signal["value"] if shelter_signal else None,
        "shelterMarketDriver": shelter_signal["driver"] if shelter_signal else None,
    }
    if write_snapshots:
        write_json(run_dir / "feed_health.json", payload)
    return payload


def feed_health_by_code(feed_health: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["itemCode"]: row for row in feed_health.get("components", [])}
