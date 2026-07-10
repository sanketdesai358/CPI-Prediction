from cpi_model.commodity_complex import COMMODITY_MAPPINGS, resolve_food_substrata, write_cut_series
from cpi_model.data import entry_by_code, forecast_universe_codes


def test_food_substrata_codes_resolve_from_registry() -> None:
    resolved = resolve_food_substrata(entry_by_code())
    assert resolved["bacon"]["itemCode"] == "SEFD01"
    assert resolved["ground_beef"]["itemCode"] == "SEFC01"
    assert resolved["fresh_whole_chicken"]["itemCode"] == "SS06011"
    assert resolved["chicken_parts"]["itemCode"] == "SS06021"
    assert resolved["eggs"]["itemCode"] == "SEFH"


def test_food_forecast_universe_uses_leaf_strata() -> None:
    codes = set(forecast_universe_codes())
    assert "SAF" not in codes
    assert "SEFC" not in codes
    assert "SEFD" not in codes
    assert {"SEFC01", "SEFC02", "SEFC03", "SEFD01", "SEFD02", "SEFD03", "SEFD04", "SEFH"} <= codes


def test_cut_series_are_stored_by_named_observation() -> None:
    feed_health = {
        "components": [
            {
                "itemCode": "SEFD01",
                "primaryFeed": "USDA pork cutout PM PDF",
                "observationsUsed": [{"date": "2026-07-06", "value": 116.24, "label": "USDA pork cutout belly"}],
            }
        ]
    }
    series = write_cut_series(feed_health)
    assert "usda_pork_cutout_belly" in series
    assert series["usda_pork_cutout_belly"]["points"][0]["value"] == 116.24


def test_each_mapping_has_a_resolved_forecast_code() -> None:
    cache = entry_by_code()
    missing = [mapping.code for mapping in COMMODITY_MAPPINGS if mapping.code not in cache]
    assert missing == []
