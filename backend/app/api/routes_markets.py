"""Market data and profitability endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.models import MarketRecord
from backend.app.schemas.schemas import (
    MarketRecordSchema,
    ProfitabilityCalculationRequest,
    ProfitabilityCalculationResponse,
)
from backend.app.services.profitability import calculate_market_profitability

router = APIRouter(prefix="/markets", tags=["Markets & Profitability"])


@router.get("", response_model=List[MarketRecordSchema])
def list_market_records(
    crop: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """List recent market price records."""
    q = db.query(MarketRecord)
    if crop:
        q = q.filter(MarketRecord.crop.ilike(f"%{crop}%"))
    records = q.order_by(MarketRecord.retrieved_at.desc()).limit(limit).all()
    return [MarketRecordSchema.model_validate(r) for r in records]


@router.post("/profitability", response_model=ProfitabilityCalculationResponse)
def calculate_profitability(payload: ProfitabilityCalculationRequest):
    """Estimate farmer net proceeds with strict transport safety rules.
    
    If transport cost is omitted, returns is_calculable=False with the exact safety disclaimer:
    'Transport cost is unknown. The most profitable market cannot be determined from price alone.'
    """
    res = calculate_market_profitability(
        market_name=payload.market_name,
        selling_price_per_kg=payload.selling_price_per_kg,
        quantity_kg=payload.quantity_kg,
        transport_cost_inr=payload.transport_cost_inr,
        loading_charges_inr=payload.loading_charges_inr,
        market_fees_inr=payload.market_fees_inr,
        packaging_costs_inr=payload.packaging_costs_inr,
    )
    return ProfitabilityCalculationResponse(**res)
