from __future__ import annotations

from cpi_excel.math import price_updated_relative_importance
from cpi_excel.ri import bls_ri_worked_example


def test_bls_relative_importance_worked_example() -> None:
    example = bls_ri_worked_example()
    actual = price_updated_relative_importance(
        example["component_dec_ri"],
        example["component_index_month"],
        example["component_index_dec"],
        example["all_items_index_month"],
        example["all_items_index_dec"],
    )
    assert round(actual, 3) == example["expected_updated_ri"]
