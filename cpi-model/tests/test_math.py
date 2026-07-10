from cpi_model.math import price_updated_relative_importance


def test_bls_relative_importance_example() -> None:
    actual = price_updated_relative_importance(7.039, 215.711, 193.306, 246.819, 241.432)
    assert round(actual, 3) == 7.683
