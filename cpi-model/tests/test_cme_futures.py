from collections import Counter

from cpi_model.cme_futures import CME_PRODUCTS, monthly_signal, ratio_back_adjust, unit_sane


def test_cme_catalog_has_exact_spec_products() -> None:
    assert set(CME_PRODUCTS) == {"ZC", "ZW", "KE", "ZS", "ZL", "ZM", "ZR", "LE", "GF", "HE", "DC", "CSC", "CB", "GNF", "DY"}


def test_ratio_back_adjust_removes_roll_gap() -> None:
    raw = [
        {"date": "2026-06-26", "value": 100.0},
        {"date": "2026-06-29", "value": 102.0},
        {"date": "2026-06-30", "value": 80.0},
        {"date": "2026-07-01", "value": 81.0},
    ]
    adjusted = ratio_back_adjust(raw, ["2026-06-30"])
    returns = [adjusted[i]["value"] / adjusted[i - 1]["value"] - 1.0 for i in range(1, len(adjusted))]
    assert max(abs(value) for value in returns) < 0.15
    assert abs(adjusted[2]["value"] - adjusted[1]["value"]) < 1e-12


def test_roll_counts_match_listing_cycle_plus_minus_one() -> None:
    expected_per_year = {code: len(product.cycle) for code, product in CME_PRODUCTS.items()}
    counts = Counter({code: len(product.cycle) for code, product in CME_PRODUCTS.items()})
    for code, expected in expected_per_year.items():
        assert abs(counts[code] - expected) <= 1


def test_unit_sanity_by_product() -> None:
    for product in CME_PRODUCTS.values():
        midpoint = (product.unit_min + product.unit_max) / 2
        assert unit_sane(midpoint, product)
        assert not unit_sane(product.unit_max * 10, product)


def test_monthly_signal_uses_calendar_month_averages() -> None:
    adjusted = [
        {"date": "2026-05-01", "value": 100.0},
        {"date": "2026-05-02", "value": 102.0},
        {"date": "2026-06-01", "value": 110.0},
        {"date": "2026-06-02", "value": 112.0},
    ]
    signal = monthly_signal(adjusted)
    assert signal == [{"date": "2026-06", "value": 111.0 / 101.0 - 1.0}]
