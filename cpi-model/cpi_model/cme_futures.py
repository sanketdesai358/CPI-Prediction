"""CME futures feed loader and continuous-series helpers.

Endpoint discovery, 2026-07-07:

The CME chart widget spec points at
`/apps/cmegroup/widgets/productLibs/esignal-charts.html?...`. The widget and
the regular product pages load public JSON from CME's `CmeWS` service. The
settlements/quotes endpoint pattern used here is:

    https://www.cmegroup.com/CmeWS/mvc/Settlements/Futures/Settlements/{product_id}/FUT
        ?strategy=DEFAULT&pageSize=500

and the quote-board pattern is:

    https://www.cmegroup.com/CmeWS/mvc/Quotes/Future/{product_id}/G?pageSize=500

In this execution environment the chart page, the `CmeWS` endpoints, and Stooq
CSV fallback all returned 403/JavaScript-verification responses. The loader
therefore records per-product blocked status rather than fabricating settles.
If CME permits the request in another runtime, the same parser/cache path will
write live payloads under `data/feeds/cme/`.
"""

from __future__ import annotations

import csv
import io
import json
import math
import re
import time
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .data import write_json
from .math import add_months


USER_AGENT = "cpi-component-dashboard/0.3 (+local research; contact: sanketsdesai.1995@gmail.com)"
CME_BASE = "https://www.cmegroup.com"
STOOQ_BASE = "https://stooq.com/q/d/l/"
MONTH_CODES = {"F": 1, "G": 2, "H": 3, "J": 4, "K": 5, "M": 6, "N": 7, "Q": 8, "U": 9, "V": 10, "X": 11, "Z": 12}


@dataclass(frozen=True)
class CmeProduct:
    code: str
    name: str
    exchange: str
    cycle: tuple[str, ...]
    unit: str
    unit_min: float
    unit_max: float
    cpi_links: tuple[str, ...]
    expected_lag_peak: str
    product_url: str
    stooq_symbol: str | None = None
    product_id: str | None = None


CME_PRODUCTS: dict[str, CmeProduct] = {
    "ZC": CmeProduct("ZC", "Corn", "XCBT", ("H", "K", "N", "U", "Z"), "cents per bushel", 100, 1500, ("SEFF", "SEFH"), "3-6", "/markets/agriculture/grains/corn.html", "zc.f", "300"),
    "ZW": CmeProduct("ZW", "SRW Wheat", "XCBT", ("H", "K", "N", "U", "Z"), "cents per bushel", 100, 2000, ("SAF111", "SEFB01"), "3-6", "/markets/agriculture/grains/wheat.html", "zw.f"),
    "KE": CmeProduct("KE", "HRW Wheat", "XCBT", ("H", "K", "N", "U", "Z"), "cents per bushel", 100, 2000, ("SAF111", "SEFB01"), "3-6", "/markets/agriculture/grains/kc-hrw-wheat.html", "ke.f"),
    "ZS": CmeProduct("ZS", "Soybeans", "XCBT", ("F", "H", "K", "N", "Q", "U", "X"), "cents per bushel", 200, 2500, ("SEFS", "SEFF", "SEFH"), "3-6", "/markets/agriculture/oilseeds/soybean.html", "zs.f"),
    "ZL": CmeProduct("ZL", "Soybean Oil", "XCBT", ("F", "H", "K", "N", "Q", "U", "V", "Z"), "cents per pound", 10, 150, ("SEFS",), "3-6", "/markets/agriculture/oilseeds/soybean-oil.html", "zl.f"),
    "ZM": CmeProduct("ZM", "Soybean Meal", "XCBT", ("F", "H", "K", "N", "Q", "U", "V", "Z"), "dollars per short ton", 100, 800, ("SEFF", "SEFH"), "3-6", "/markets/agriculture/oilseeds/soybean-meal.html", "zm.f"),
    "ZR": CmeProduct("ZR", "Rough Rice", "XCBT", ("F", "H", "K", "N", "U", "X"), "cents per cwt", 500, 4000, ("SEFA",), "3-6", "/markets/agriculture/grains/rough-rice.html", "zr.f"),
    "LE": CmeProduct("LE", "Live Cattle", "XCME", ("G", "J", "M", "Q", "V", "Z"), "cents per pound", 50, 300, ("SEFC",), "2-3", "/markets/agriculture/livestock/live-cattle.html", "le.f"),
    "GF": CmeProduct("GF", "Feeder Cattle", "XCME", ("F", "H", "J", "K", "Q", "U", "V", "X"), "cents per pound", 50, 400, ("SEFC",), "3-6", "/markets/agriculture/livestock/feeder-cattle.html", "gf.f"),
    "HE": CmeProduct("HE", "Lean Hogs", "XCME", ("G", "J", "K", "M", "N", "Q", "V", "Z"), "cents per pound", 20, 200, ("SEFD",), "2-3", "/markets/agriculture/livestock/lean-hogs.html", "he.f"),
    "DC": CmeProduct("DC", "Class III Milk", "XCME", tuple(MONTH_CODES), "dollars per cwt", 5, 40, ("SEFJ", "SEFJ01"), "0-forward", "/markets/agriculture/dairy/class-iii-milk.html", "dc.f"),
    "CSC": CmeProduct("CSC", "Cash-settled Cheese", "XCME", tuple(MONTH_CODES), "dollars per pound", 0.5, 5, ("SEFJ02",), "0-forward", "/markets/agriculture/dairy/cheese.html"),
    "CB": CmeProduct("CB", "Cash-settled Butter", "XCME", tuple(MONTH_CODES), "dollars per pound", 0.5, 5, ("SEFJ", "SEFS"), "0-forward", "/markets/agriculture/dairy/butter.html", "cb.f"),
    "GNF": CmeProduct("GNF", "Nonfat Dry Milk", "XCME", tuple(MONTH_CODES), "dollars per pound", 0.2, 4, ("SEFJ",), "0-forward", "/markets/agriculture/dairy/nonfat-dry-milk.html"),
    "DY": CmeProduct("DY", "Dry Whey", "XCME", tuple(MONTH_CODES), "dollars per pound", 0.1, 2, ("SEFJ",), "0-forward", "/markets/agriculture/dairy/dry-whey.html"),
}


def _fetch(url: str, *, accept: str = "application/json,text/plain,*/*", timeout: int = 6) -> tuple[bytes | None, str | None, int | None]:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": accept})
    try:
        with urlopen(request, timeout=timeout) as response:
            return response.read(), None, response.status
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:220]
        return None, f"HTTP {exc.code}: {body}", exc.code
    except URLError as exc:
        return None, f"URL error: {exc.reason}", None
    except TimeoutError:
        return None, "timeout", None
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}", None


def cme_settlements_url(product: CmeProduct, trade_date: str | None = None) -> str | None:
    if not product.product_id:
        return None
    params: dict[str, Any] = {"strategy": "DEFAULT", "pageSize": 500}
    if trade_date:
        params["tradeDate"] = trade_date
    return f"{CME_BASE}/CmeWS/mvc/Settlements/Futures/Settlements/{product.product_id}/FUT?{urlencode(params)}"


def verify_product_cycle(product: CmeProduct, *, skip_live: bool = False) -> dict[str, Any]:
    url = f"{CME_BASE}{product.product_url}"
    if skip_live:
        return {"status": "blocked", "url": url, "error": "Skipped live cycle verification after CME blocked/reset prior requests in this run.", "verifiedCycle": None}
    raw, error, status_code = _fetch(url, accept="text/html,application/xhtml+xml,*/*")
    if not raw:
        return {"status": "blocked", "url": url, "error": error, "verifiedCycle": None}
    text = raw.decode("utf-8", errors="replace")
    cycle_hits = [code for code in product.cycle if re.search(rf"\b{code}\d\b", text)]
    verified = tuple(cycle_hits) == product.cycle if cycle_hits else None
    return {"status": "verified" if verified else "unverified", "url": url, "error": None if verified else "Could not verify listing cycle in product-page HTML.", "verifiedCycle": cycle_hits}


def parse_cme_settlements(payload: bytes, product: CmeProduct) -> list[dict[str, Any]]:
    data = json.loads(payload.decode("utf-8"))
    rows = data.get("settlements") or data.get("quotes") or data.get("data") or []
    parsed: list[dict[str, Any]] = []
    for row in rows:
        month = str(row.get("month") or row.get("contractMonth") or row.get("monthYear") or "")
        settle_raw = row.get("settle") or row.get("last") or row.get("priorSettle")
        if settle_raw in {None, "", "-"}:
            continue
        try:
            settle = float(str(settle_raw).replace(",", ""))
        except ValueError:
            continue
        parsed.append({"contract": month, "settle": settle, "unit": product.unit})
    return parsed


def fetch_stooq_history(product: CmeProduct) -> tuple[list[dict[str, Any]], str | None]:
    if not product.stooq_symbol:
        return [], "No Stooq symbol configured for this product."
    raw, error, _ = _fetch(f"{STOOQ_BASE}?{urlencode({'s': product.stooq_symbol, 'i': 'd'})}", accept="text/csv,text/plain,*/*")
    if not raw:
        return [], error
    text = raw.decode("utf-8", errors="replace")
    if "<html" in text.lower() or "requires javascript" in text.lower():
        return [], "Stooq fallback is JavaScript-gated from this environment."
    rows = []
    for row in csv.DictReader(io.StringIO(text)):
        try:
            close = float(row.get("Close") or "")
        except ValueError:
            continue
        rows.append({"date": row["Date"], "value": close})
    return rows, None if rows else "Stooq returned no parseable close history."


def unit_sane(value: float, product: CmeProduct) -> bool:
    return product.unit_min <= value <= product.unit_max


def business_days_before(day: date, count: int) -> date:
    current = day
    remaining = count
    while remaining:
        current -= timedelta(days=1)
        if current.weekday() < 5:
            remaining -= 1
    return current


def contract_month_date(contract: str) -> date | None:
    match = re.search(r"([FGHJKMNQUVXZ])(\d{1,2})", contract.upper())
    if not match:
        return None
    year_digit = int(match.group(2))
    year = 2020 + year_digit if year_digit < 30 else 2000 + year_digit
    return date(year, MONTH_CODES[match.group(1)], 1)


def roll_date_for_contract(contract: str) -> str | None:
    month_date = contract_month_date(contract)
    if not month_date:
        return None
    expiry_proxy = add_months(month_date.isoformat()[:7], 1) + "-01"
    expiry = datetime.fromisoformat(expiry_proxy).date() - timedelta(days=1)
    return business_days_before(expiry, 10).isoformat()


def ratio_back_adjust(front_series: list[dict[str, Any]], roll_dates: list[str]) -> list[dict[str, Any]]:
    if not front_series:
        return []
    ordered = sorted(front_series, key=lambda item: item["date"])
    adjusted = [{"date": row["date"], "value": float(row["value"])} for row in ordered]
    roll_set = set(roll_dates)
    factor = 1.0
    prior_value = adjusted[0]["value"]
    for row in adjusted:
        raw = row["value"]
        if row["date"] in roll_set and raw not in {0, prior_value}:
            factor *= prior_value / raw
        row["value"] = raw * factor
        prior_value = row["value"]
    return adjusted


def monthly_signal(adjusted_points: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_month: dict[str, list[float]] = {}
    for point in adjusted_points:
        by_month.setdefault(point["date"][:7], []).append(float(point["value"]))
    averages = [{"date": month, "value": sum(values) / len(values)} for month, values in sorted(by_month.items())]
    out = []
    for prior, current in zip(averages, averages[1:]):
        if prior["value"]:
            out.append({"date": current["date"], "value": current["value"] / prior["value"] - 1.0})
    return out


def fetch_product(product: CmeProduct, cache_dir: Path, *, write_snapshots: bool = False, skip_cme_live: bool = False, skip_stooq_live: bool = False) -> dict[str, Any]:
    cycle = verify_product_cycle(product, skip_live=skip_cme_live)
    endpoint_url = cme_settlements_url(product)
    endpoint_error = "No CME product id resolved from public product page." if endpoint_url is None else None
    settlements: list[dict[str, Any]] = []
    cache_path = cache_dir / "raw" / f"{product.code}_cme_settlements.json"
    if endpoint_url and not skip_cme_live:
        raw, endpoint_error, _ = _fetch(endpoint_url)
        if not raw and cache_path.exists():
            raw = cache_path.read_bytes()
            endpoint_error = "Loaded cached CME settlement payload because live endpoint was unavailable."
        if raw:
            if write_snapshots:
                write_json(cache_path, json.loads(raw.decode("utf-8")))
            try:
                settlements = parse_cme_settlements(raw, product)
            except Exception as exc:
                endpoint_error = f"CME parser error: {type(exc).__name__}: {exc}"
    stooq_points, stooq_error = ([], "Skipped Stooq fallback after JavaScript verification blocked prior requests in this run.") if skip_stooq_live else fetch_stooq_history(product)
    status = "live" if settlements else "fallback" if stooq_points else "blocked"
    last_settle = None
    last_settle_date = None
    raw_deferred = settlements[:3]
    if settlements:
        last_settle = settlements[0]["settle"]
        last_settle_date = datetime.now(timezone.utc).date().isoformat()
    elif stooq_points:
        latest = stooq_points[-1]
        last_settle = latest["value"]
        last_settle_date = latest["date"]
    if last_settle is not None and not unit_sane(float(last_settle), product):
        status = "failed_sanity"
    last_roll = None
    if raw_deferred:
        last_roll = roll_date_for_contract(str(raw_deferred[0].get("contract") or ""))
    return {
        "code": product.code,
        "name": product.name,
        "exchange": product.exchange,
        "status": status,
        "endpoint": endpoint_url,
        "fallback": bool(stooq_points and not settlements),
        "lastSettleDate": last_settle_date,
        "lastSettle": last_settle,
        "lastRollDate": last_roll,
        "unit": product.unit,
        "cycle": list(product.cycle),
        "cycleVerification": cycle,
        "rawDeferred": raw_deferred,
        "points": stooq_points,
        "historySpan": {"start": stooq_points[0]["date"], "end": stooq_points[-1]["date"]} if stooq_points else None,
        "error": None if status == "live" else "; ".join(filter(None, [endpoint_error, stooq_error, cycle.get("error")])),
    }


def collect_cme_futures(cache_dir: Path, *, write_snapshots: bool = False) -> dict[str, Any]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    products = []
    skip_cme_live = False
    skip_stooq_live = False
    for product in CME_PRODUCTS.values():
        row = fetch_product(
            product,
            cache_dir,
            write_snapshots=write_snapshots,
            skip_cme_live=skip_cme_live,
            skip_stooq_live=skip_stooq_live,
        )
        products.append(row)
        error_text = row.get("error") or ""
        if "HTTP 403" in error_text or "ConnectionResetError" in error_text or "timeout" in error_text:
            skip_cme_live = True
        if "JavaScript-gated" in error_text or "requires JavaScript" in error_text:
            skip_stooq_live = True
        time.sleep(0.15)
    if write_snapshots:
        write_json(cache_dir / "cme_futures.json", {"generatedAt": datetime.now(timezone.utc).isoformat(), "products": products})
    observations = [
        {"date": row["lastSettleDate"], "value": row["lastSettle"], "label": f"CME {row['code']} {row['name']}"}
        for row in products
        if row.get("lastSettleDate") and row.get("lastSettle") is not None
    ]
    live = [row for row in products if row["status"] == "live"]
    fallback = [row for row in products if row["fallback"]]
    status = "live" if len(live) == len(products) else "partial_live_fallback" if live or fallback else "blocked"
    latest = max(observations, key=lambda item: item["date"]) if observations else None
    return {
        "feed": "CME futures settles",
        "status": status,
        "lastObservationDate": latest["date"] if latest else None,
        "latestValue": latest["value"] if latest else None,
        "unit": "various",
        "observations": observations,
        "points": [],
        "products": products,
        "error": None if status == "live" else "CME endpoint and Stooq fallback are blocked/unavailable for one or more products.",
    }


def food_futures_lag_report(cme_payload: dict[str, Any]) -> dict[str, Any]:
    products = cme_payload.get("products") or []
    active = [row["code"] for row in products if row.get("status") == "live"]
    rows = []
    for component, features, expected_peak in [
        ("SEFC", ["LE", "GF"], "2-3 / 3-6"),
        ("SEFD", ["HE"], "2-3"),
        ("SEFF", ["ZC", "ZM"], "3-6"),
        ("SEFH", ["ZC", "ZM"], "3-6"),
        ("SEFJ", ["DC", "CSC", "CB", "GNF", "DY"], "0-forward"),
        ("SEFS", ["ZS", "ZL"], "3-6"),
        ("SAF111", ["ZW", "KE"], "3-6"),
    ]:
        available = [code for code in features if code in active]
        rows.append(
            {
                "component": component,
                "features": features,
                "availableFeatures": available,
                "kept": bool(available),
                "decision": "dropped_no_live_futures_history" if not available else "pending_window_c_estimation",
                "expectedLagPeak": expected_peak,
                "lagProfile": [{"lag": lag, "weight": None} for lag in range(7)],
                "windowC": {"withoutFuturesMae": None, "withFuturesMae": None, "winner": "without_futures" if not available else "pending"},
            }
        )
    return {
        "status": "blocked_no_live_history" if not active else "pending_estimation",
        "rows": rows,
        "notes": "No fitted ridge profiles are reported until live or cached futures histories are available; USDA food feeds remain primary.",
    }
