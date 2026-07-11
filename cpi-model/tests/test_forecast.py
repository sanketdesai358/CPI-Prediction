from cpi_model.forecast import aggregate, build_forecast, forecast_component
from cpi_model.data import ancestor_pairs, cache_entries, forecast_universe_codes
from cpi_model.triage import build_extended_registry


_FORECAST_PAYLOAD = None


def forecast_payload() -> dict:
    global _FORECAST_PAYLOAD
    if _FORECAST_PAYLOAD is None:
        _FORECAST_PAYLOAD = build_forecast("2026-06")
    return _FORECAST_PAYLOAD


def test_leaf_relative_importance_sums_to_headline() -> None:
    extended = build_extended_registry()
    total = sum(float(row.get("model_weight") or 0.0) for row in extended)
    assert 99.5 <= total <= 100.5


def test_forecast_universe_has_no_ancestor_descendant_pairs() -> None:
    codes = forecast_universe_codes()
    assert ancestor_pairs(codes) == []


def test_aggregation_identity() -> None:
    payload = forecast_payload()
    total_pp = sum(row["contribution_pp"] for row in payload["components"])
    assert abs(payload["headline"]["nsaMm"] - total_pp / 100.0) < 1e-12


def test_latest_projection_components_cover_all_leaf_components() -> None:
    payload = forecast_payload()
    projections = {row["itemCode"]: row for row in payload["projectionComponents"]}
    children: dict[str, list[dict]] = {}
    entries = cache_entries()
    by_code = {entry["itemCode"]: entry for entry in entries}
    for entry in entries:
        if entry.get("parent"):
            children.setdefault(entry["parent"], []).append(entry)
    offenders = []
    for entry in entries:
        if children.get(entry["itemCode"]):
            continue
        if entry.get("currentRi") is None or not entry.get("history"):
            continue
        row = projections.get(entry["itemCode"])
        if not row or row.get("forecast_sa_mm") is None or not row.get("projectionSource"):
            offenders.append(f"{entry['itemCode']} {entry['name']}")
    assert offenders == []


def test_projection_display_resolves_oer_parent_child_duplicate() -> None:
    payload = forecast_payload()
    projections = {row["itemCode"]: row for row in payload["projectionComponents"]}
    assert projections["SEHC"]["forecast_sa_mm"] is not None
    assert projections["SEHC"]["displayInHeatmap"] is True
    assert projections["SEHC01"]["forecast_sa_mm"] is not None
    assert projections["SEHC01"]["displayInHeatmap"] is False


def test_shelter_uses_tier1_cpi_history_fallback_not_external_rent_overlay() -> None:
    payload = forecast_payload()
    components = {row["itemCode"]: row for row in payload["components"]}
    for code in ("SEHA", "SEHC"):
        assert components[code]["tier"] == 1
        assert "free fallback: recent CPI-timed movement" in components[code]["driverSnapshot"]
        assert "external rent overlay" not in components[code]["driverSnapshot"]
        assert "Zillow" not in components[code]["driverSnapshot"]
        assert components[code].get("feedStatus") is None
    projections = {row["itemCode"]: row for row in payload["projectionComponents"]}
    sehc01 = projections["SEHC01"]
    assert sehc01["projectionSource"] == "model"
    assert "free fallback: recent CPI-timed movement" in sehc01["projectionSourceDetail"]
    assert "external rent overlay" not in sehc01["projectionSourceDetail"]
    assert "Zillow" not in sehc01["projectionSourceDetail"]


def test_airline_fares_use_guarded_jet_fuel_signal() -> None:
    entry = {
        "itemCode": "SETG01",
        "name": "Airline fares",
        "history": [
            {"month": "2025-06", "nsaIndex": 100.0, "saMm": 0.01},
            {"month": "2025-07", "nsaIndex": 102.0, "saMm": 0.02},
            {"month": "2025-08", "nsaIndex": 101.0, "saMm": -0.01},
            {"month": "2025-09", "nsaIndex": 103.0, "saMm": 0.02},
            {"month": "2025-10", "nsaIndex": 104.0, "saMm": 0.01},
            {"month": "2025-11", "nsaIndex": 105.0, "saMm": 0.01},
            {"month": "2025-12", "nsaIndex": 106.0, "saMm": 0.01},
            {"month": "2026-01", "nsaIndex": 108.0, "saMm": 0.02},
            {"month": "2026-02", "nsaIndex": 110.0, "saMm": 0.02},
            {"month": "2026-03", "nsaIndex": 112.0, "saMm": 0.02},
            {"month": "2026-04", "nsaIndex": 114.0, "saMm": 0.02},
            {"month": "2026-05", "nsaIndex": 116.0, "saMm": 0.02},
        ],
    }
    model = {"tier": 1, "model_type": "airfare_fare_mix_proxy"}
    feed = {"jetFuelNsaMm": -0.2265, "jetFuelDriver": "EIA jet fuel test move"}
    live, driver = forecast_component(entry, model, "2026-06", feed)
    fallback, _ = forecast_component(entry, model, "2026-06", None)
    assert live < fallback
    assert live == max(fallback + 0.12 * feed["jetFuelNsaMm"], -0.08)
    assert "guarded jet-fuel pass-through" in driver


def test_lodging_uses_costar_primary_and_seasonal_ar_only_on_outage() -> None:
    entry = next(row for row in cache_entries() if row["itemCode"] == "SEHB")
    model = {"tier": 1, "model_type": "costar_adr_pass_through"}
    live, live_driver = forecast_component(
        entry,
        model,
        "2026-06",
        {"lodgingNsaMm": 0.0203, "lodgingDriver": "CoStar/STR ADR test"},
    )
    fallback, fallback_driver = forecast_component(entry, model, "2026-06", None)
    assert live == 0.0203
    assert "CoStar/STR ADR test" in live_driver
    assert fallback != live
    assert "feed outage" in fallback_driver
    assert "Tier 3 Seasonal AR" in fallback_driver
