from __future__ import annotations

from cpi_model.data import entry_by_code
from cpi_model.energy_liquids import fit_zero_intercept_beta, measurement_forecast
from cpi_model.forecast import forecast_component


def test_zero_intercept_beta_uses_only_prior_months() -> None:
    measurements = {f"2024-{month:02d}": month / 100.0 for month in range(1, 13)}
    actuals = {month: 0.8 * value for month, value in measurements.items()}
    actuals["2024-12"] = 99.0
    beta, observations = fit_zero_intercept_beta(
        actuals,
        measurements,
        "2024-12",
        lower=0.5,
        upper=1.15,
        default=0.9,
        min_observations=6,
    )
    assert observations == 11
    assert abs(beta - 0.8) < 1e-12


def test_june_liquid_measurements_replace_wrong_sign_fallbacks() -> None:
    entries = entry_by_code()
    diesel, diesel_diag = measurement_forecast(entries["SETB02"], "2026-06", "diesel", -0.10281275113849453)
    heating, heating_diag = measurement_forecast(entries["SEHE01"], "2026-06", "heating_oil", -0.13179040055897195)
    assert diesel < -0.08
    assert heating < -0.05
    assert 0.5 <= diesel_diag["beta"] <= 1.15
    assert 0.2 <= heating_diag["beta"] <= 0.9


def test_forecast_component_uses_liquid_measurement_feed() -> None:
    entry = entry_by_code()["SETB02"]
    forecast, driver = forecast_component(
        entry,
        {"tier": 1, "model_type": "measurement_pass_through_diesel"},
        "2026-06",
        {
            "liquidMeasurementNsaMm": -0.10281275113849453,
            "liquidMeasurementSeries": "diesel",
            "liquidMeasurementDriver": "EIA diesel test measurement",
        },
    )
    assert forecast < -0.08
    assert "fitted retail pass-through beta" in driver
