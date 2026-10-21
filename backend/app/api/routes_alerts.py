"""Price alert management and evaluation API endpoints."""

from datetime import datetime, timezone
import json
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.models import PriceAlert
from backend.app.schemas.schemas import PriceAlertResponse
from backend.app.services.alert_service import AlertService

router = APIRouter(prefix="/alerts", tags=["Price Alerts"])


@router.get("", response_model=List[PriceAlertResponse])
def list_alerts(db: Session = Depends(get_db)):
    """List all registered price alerts with their evaluation status."""
    alerts = db.query(PriceAlert).order_by(PriceAlert.created_at.desc()).all()
    results = []
    for a in alerts:
        results.append(
            PriceAlertResponse(
                id=a.id,
                alert_id=a.alert_id,
                query_id=a.query_id,
                crop=a.crop,
                market=a.market,
                target_price=a.target_price,
                unit=a.unit,
                threshold_direction=a.threshold_direction,
                status=a.status,
                is_simulated=a.is_simulated,
                created_at=a.created_at,
                triggered_at=a.triggered_at,
                evaluation_history=json.loads(a.evaluation_history or "[]"),
            )
        )
    return results


@router.post("/simulate-evaluate")
def simulate_alert_evaluation(db: Session = Depends(get_db)):
    """Simulate checking active price alerts against simulated market arrivals."""
    sample_records = [
        {"crop": "tomato", "market_name": "Dharmapuri Regulated Market", "normalized_modal_price_per_kg": 21.0},
        {"crop": "tomato", "market_name": "Palacode APMC", "normalized_modal_price_per_kg": 23.5},
        {"crop": "onion", "market_name": "Dharmapuri Regulated Market", "normalized_modal_price_per_kg": 35.0},
    ]
    triggered = AlertService.evaluate_alerts_against_records(db, sample_records)
    return {
        "status": "success",
        "alerts_triggered_count": len(triggered),
        "triggered_details": triggered,
        "note": "Evaluation performed in simulation demo mode.",
    }
