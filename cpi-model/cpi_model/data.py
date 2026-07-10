from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from .math import add_months, pct_change
from .paths import DASHBOARD_CACHE_PATH, EXTENDED_REGISTRY_PATH, REGISTRY_PATH


@lru_cache(maxsize=1)
def load_dashboard_cache() -> dict[str, Any]:
    return json.loads(DASHBOARD_CACHE_PATH.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load_registry(*, extended: bool = False) -> list[dict[str, Any]]:
    path = EXTENDED_REGISTRY_PATH if extended and EXTENDED_REGISTRY_PATH.exists() else REGISTRY_PATH
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, allow_nan=False), encoding="utf-8")


def cache_entries() -> list[dict[str, Any]]:
    return load_dashboard_cache()["entries"]


def entry_by_code() -> dict[str, dict[str, Any]]:
    return {entry["itemCode"]: entry for entry in cache_entries()}


def latest_month() -> str:
    return load_dashboard_cache()["refMonth"]


def next_unpublished_month() -> str:
    return add_months(latest_month(), 1)


def history_mm(entry: dict[str, Any], *, seasonal: bool = False) -> list[tuple[str, float | None]]:
    key = "saMm" if seasonal else "nsaMm"
    out: list[tuple[str, float | None]] = []
    for point in entry["history"]:
        if key == "nsaMm":
            current = point.get("nsaIndex")
            prior_point = next(
                (item for item in entry["history"] if item["month"] == add_months(point["month"], -1)),
                None,
            )
            value = pct_change(current, prior_point.get("nsaIndex") if prior_point else None)
        else:
            value = point.get("saMm")
        out.append((point["month"], value))
    return out


MAJOR_GROUP_ROOTS = ["SAF", "SAH", "SAA", "SAT", "SAM", "SAR", "SAE", "SAG"]


def children_by_parent(entries: list[dict[str, Any]] | None = None) -> dict[str, list[dict[str, Any]]]:
    rows = entries or cache_entries()
    children: dict[str, list[dict[str, Any]]] = {}
    for entry in rows:
        parent = entry.get("parent")
        if parent:
            children.setdefault(parent, []).append(entry)
    return children


def forecast_universe_codes(entries: list[dict[str, Any]] | None = None) -> list[str]:
    """Return a non-overlapping CPI coverage partition using published RI coverage.

    BLS publishes many overlapping special aggregates plus some lower-level rows with no
    monthly RI. We descend only when children cover the parent RI tightly; otherwise the
    parent remains the forecast unit. This gives contribution rows with no
    ancestor/descendant pairs and current RI coverage near 100.
    """
    rows = entries or cache_entries()
    by_code = {entry["itemCode"]: entry for entry in rows}
    children = children_by_parent(rows)

    def usable_child(child: dict[str, Any]) -> bool:
        code = child["itemCode"]
        name = child["name"].lower()
        if child.get("currentRi") is None:
            return False
        if name.startswith("purchasing power"):
            return False
        # Avoid special overlapping all-items-less aggregates in the expenditure tree.
        if code.startswith("SA0L"):
            return False
        return True

    def is_food_branch(entry: dict[str, Any]) -> bool:
        code = entry["itemCode"]
        name = entry["name"].lower()
        return code.startswith(("SAF", "SEF", "SSF")) or "food" in name or "alcoholic beverage" in name

    def choose(code: str) -> list[str]:
        entry = by_code.get(code)
        if not entry:
            return []
        kids = [kid for kid in children.get(code, []) if usable_child(kid)]
        if not kids:
            return [code]
        parent_ri = float(entry.get("currentRi") or 0.0)
        child_ri = sum(float(kid.get("currentRi") or 0.0) for kid in kids)
        if is_food_branch(entry) and parent_ri > 0 and 0.65 * parent_ri <= child_ri <= 1.45 * parent_ri:
            out: list[str] = []
            for kid in kids:
                out.extend(choose(kid["itemCode"]))
            return out
        if parent_ri > 0 and 0.98 * parent_ri <= child_ri <= 1.02 * parent_ri:
            out: list[str] = []
            for kid in kids:
                out.extend(choose(kid["itemCode"]))
            return out
        return [code]

    selected: list[str] = []
    for root in MAJOR_GROUP_ROOTS:
        selected.extend(choose(root))
    return selected


def ancestor_pairs(codes: list[str], entries: list[dict[str, Any]] | None = None) -> list[tuple[str, str]]:
    rows = entries or cache_entries()
    by_code = {entry["itemCode"]: entry for entry in rows}
    selected = set(codes)
    pairs: list[tuple[str, str]] = []
    for code in codes:
        parent = by_code.get(code, {}).get("parent")
        while parent:
            if parent in selected:
                pairs.append((parent, code))
            parent = by_code.get(parent, {}).get("parent")
    return pairs


def current_model_components(entries: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Forecast units with real BLS current RI and no overlapping ancestors."""
    rows = entries or cache_entries()
    selected = set(forecast_universe_codes(rows))
    return [
        entry
        for entry in rows
        if entry["itemCode"] in selected
        and entry.get("currentRi") is not None
        and entry.get("seriesNsa")
        and entry.get("history")
    ]
