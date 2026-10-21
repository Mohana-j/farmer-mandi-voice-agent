"""Tests for profitability safety rules and net proceeds calculation."""

import pytest
from backend.app.services.profitability import (
    UNKNOWN_TRANSPORT_DISCLAIMER,
    calculate_market_profitability,
)


def test_missing_transport_cost_blocks_calculation():
    # If transport cost is missing, must not calculate net proceeds or claim most profitable
    res = calculate_market_profitability(
        market_name="Krishnagiri Market",
        selling_price_per_kg=25.0,
        quantity_kg=500.0,
        transport_cost_inr=None,
    )
    assert res["is_calculable"] is False
    assert res["disclaimer"] == UNKNOWN_TRANSPORT_DISCLAIMER
    assert res["gross_revenue_inr"] is None
    assert res["estimated_net_proceeds_inr"] is None
    assert "cannot be determined from price alone" in res["disclaimer"]


def test_complete_inputs_calculate_accurate_net_proceeds():
    # Selling 1,000 kg @ ₹24/kg = ₹24,000 gross
    # Transport: ₹2,000, Loading: ₹400, Market fee: ₹200, Packaging: ₹400 = Total costs: ₹3,000
    # Net proceeds = ₹21,000
    res = calculate_market_profitability(
        market_name="Dharmapuri Regulated Market",
        selling_price_per_kg=24.0,
        quantity_kg=1000.0,
        transport_cost_inr=2000.0,
        loading_charges_inr=400.0,
        market_fees_inr=200.0,
        packaging_costs_inr=400.0,
    )
    assert res["is_calculable"] is True
    assert res["gross_revenue_inr"] == 24000.0
    assert res["total_estimated_costs_inr"] == 3000.0
    assert res["estimated_net_proceeds_inr"] == 21000.0
    assert "estimate based on farmer-supplied expenses" in res["disclaimer"]
