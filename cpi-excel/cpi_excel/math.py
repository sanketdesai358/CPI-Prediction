from __future__ import annotations


def price_updated_relative_importance(
    component_dec_ri: float,
    component_index_month: float,
    component_index_dec: float,
    all_items_index_month: float,
    all_items_index_dec: float,
) -> float:
    """BLS relative-importance price update, normalized so all items = 100."""
    component_updated_weight = component_dec_ri * (
        component_index_month / component_index_dec
    )
    all_items_updated_weight = 100.0 * (
        all_items_index_month / all_items_index_dec
    )
    return 100.0 * component_updated_weight / all_items_updated_weight


def one_month_contribution(prior_relative_importance: float, current: float, prior: float) -> float:
    """Approximate one-month contribution in percentage points."""
    return prior_relative_importance * ((current / prior) - 1.0)
