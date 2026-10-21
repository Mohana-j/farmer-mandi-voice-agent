"""Profitability safety and net proceeds estimation engine.

Strict Rule: Never claim highest-price market is most profitable when transport costs are unknown.
"""

from typing import Any, Dict, Optional


UNKNOWN_TRANSPORT_DISCLAIMER = (
    "Transport cost is unknown. The most profitable market cannot be determined from price alone."
)


def calculate_market_profitability(
    market_name: str,
    selling_price_per_kg: float,
    quantity_kg: float,
    transport_cost_inr: Optional[float] = None,
    loading_charges_inr: float = 0.0,
    market_fees_inr: float = 0.0,
    packaging_costs_inr: float = 0.0,
    other_expenses_inr: float = 0.0,
) -> Dict[str, Any]:
    """Calculate net proceeds only when transport costs are explicitly supplied.
    
    If transport cost is None or omitted, strictly returns is_calculable=False
    with the exact required safety disclaimer.
    """
    if transport_cost_inr is None:
        return {
            "is_calculable": False,
            "market_name": market_name,
            "disclaimer": UNKNOWN_TRANSPORT_DISCLAIMER,
            "gross_revenue_inr": None,
            "total_estimated_costs_inr": None,
            "estimated_net_proceeds_inr": None,
            "cost_breakdown": None,
            "safety_note": "A higher market price may be offset by distance, vehicle hire, toll charges, or market commission.",
        }

    # All necessary inputs are present
    gross_revenue = round(selling_price_per_kg * quantity_kg, 2)
    total_costs = round(
        transport_cost_inr
        + loading_charges_inr
        + market_fees_inr
        + packaging_costs_inr
        + other_expenses_inr,
        2,
    )
    net_proceeds = round(gross_revenue - total_costs, 2)

    return {
        "is_calculable": True,
        "market_name": market_name,
        "disclaimer": "This is an estimate based on farmer-supplied expenses, not a profit guarantee.",
        "gross_revenue_inr": gross_revenue,
        "total_estimated_costs_inr": total_costs,
        "estimated_net_proceeds_inr": net_proceeds,
        "cost_breakdown": {
            "transport_cost": round(transport_cost_inr, 2),
            "loading_charges": round(loading_charges_inr, 2),
            "market_fees": round(market_fees_inr, 2),
            "packaging_costs": round(packaging_costs_inr, 2),
            "other_expenses": round(other_expenses_inr, 2),
        },
        "safety_note": "Prices fluctuate throughout trading hours. Verify fees at market gate.",
    }
