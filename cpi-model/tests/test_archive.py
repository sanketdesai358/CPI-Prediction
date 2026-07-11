from __future__ import annotations

from cpi_model.archive import build_prediction_rows, challenger_path, current_components, production_driver_inputs, read_json
from cpi_model.paths import DASHBOARD_ROOT


def test_archive_predictions_are_complete_for_current_forecast() -> None:
    forecast = read_json(DASHBOARD_ROOT / "src" / "data" / "forecast" / "latest-forecast.json")
    challenger = read_json(challenger_path())
    month = forecast["forecastMonth"]
    rows = build_prediction_rows(month, "test-run", forecast, challenger)
    component_count = len(current_components())
    assert len(rows) == component_count * 4
    assert {row["model"] for row in rows} == {"production", "hrnn", "i_gru", "seasonal_ar"}
    assert all(row["fallback_level"] for row in rows)
    assert all(row["predicted_nsa_mm"] is not None for row in rows)
    assert all(row["predicted_sa_mm"] is not None for row in rows)


def test_archive_uses_non_overlapping_component_set() -> None:
    components = current_components()
    selected = {entry["itemCode"] for entry in components}
    by_code = {entry["itemCode"]: entry for entry in components}
    overlaps = []
    for code in selected:
        parent = by_code.get(code, {}).get("parent")
        while parent:
            if parent in selected:
                overlaps.append((parent, code))
            parent = by_code.get(parent, {}).get("parent")
    assert overlaps == []


def test_archive_records_each_costar_weekly_adr_print() -> None:
    row = {
        "itemCode": "SEHB",
        "inputSeries": ["CoStar/STR weekly U.S. ADR"],
        "driverSnapshot": "CoStar ADR primary",
        "feedStatus": {
            "lodgingModel": {"adrBeta": 0.25},
            "observationsUsed": [
                {
                    "date": "2026-06-20",
                    "publicationDate": "2026-06-25",
                    "value": 178.03,
                    "occupancy": 71.3,
                    "url": "https://example.test/week",
                }
            ],
        },
    }
    inputs = production_driver_inputs(row, "2026-06", "test-run")
    weekly = [item for item in inputs if item["input_name"] == "costar_str_weekly_adr_2026-06-20"]
    assert len(weekly) == 1
    assert weekly[0]["input_publish_date"] == "2026-06-25"
    assert weekly[0]["beta_or_weight_applied"] == 0.25
