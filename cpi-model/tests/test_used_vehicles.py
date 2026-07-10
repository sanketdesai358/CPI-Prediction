from cpi_model.used_vehicles import SELECTED_MANHEIM_LAGS, forecast_seta02_sa, load_lag_weights


def test_seta02_uses_parsimonious_lag_0_2_kernel() -> None:
    weights = load_lag_weights()
    betas = weights["manheim_lag_weights"]
    assert SELECTED_MANHEIM_LAGS == [0, 2]
    assert 0.30 <= sum(float(betas[f"m{lag}"]) for lag in SELECTED_MANHEIM_LAGS) <= 0.50


def test_seta02_forecast_uses_sa_history_and_manheim_lag_0_2() -> None:
    entry = {
        "history": [
            {"month": "2025-12", "saIndex": 100.0, "saMm": 0.001},
            {"month": "2026-01", "saIndex": 100.2, "saMm": 0.002},
            {"month": "2026-02", "saIndex": 100.0, "saMm": -0.002},
            {"month": "2026-03", "saIndex": 100.3, "saMm": 0.003},
            {"month": "2026-04", "saIndex": 100.4, "saMm": 0.001},
            {"month": "2026-05", "saIndex": 100.5, "saMm": 0.001},
        ]
    }
    feed = {
        "points": [
            {"date": "2026-03", "value": 200.0},
            {"date": "2026-04", "value": 198.0},
            {"date": "2026-05", "value": 199.0},
            {"date": "2026-06", "value": 201.0},
        ]
    }
    result = forecast_seta02_sa(entry, "2026-06", feed)
    assert result is not None
    forecast, driver = result
    assert isinstance(forecast, float)
    assert "Manheim m0, m2 signal" in driver
    assert "m1" not in driver
