"""Price alert creation, approval preview, and simulated evaluation service."""

from datetime import datetime, timezone
import json
from typing import Any, Dict, List, Optional
import uuid
from sqlalchemy.orm import Session

from backend.app.models.models import PriceAlert


class AlertService:
    @staticmethod
    def prepare_alert_preview(
        crop: str,
        market: str,
        target_price: float,
        unit: str = "INR/kg",
        threshold_direction: str = "below",
        query_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate preview of price alert before human approval."""
        summary = (
            f"Set price alert for {crop.capitalize()} at {market}: "
            f"Trigger when modal price goes {threshold_direction} ₹{target_price:.2f}/{unit}. "
            f"Notification channel: Simulated In-App Notification (Demo Mode)."
        )

        return {
            "query_id": query_id,
            "crop": crop.capitalize(),
            "market": market,
            "target_price": target_price,
            "unit": unit,
            "threshold_direction": threshold_direction,
            "summary_of_changes": summary,
            "channel": "Simulated In-App Push",
            "is_simulated": True,
        }

    @staticmethod
    def execute_and_verify_alert(
        db: Session,
        alert_id: str,
        crop: str,
        market: str,
        target_price: float,
        unit: str = "INR/kg",
        threshold_direction: str = "below",
        query_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create price alert in database and perform independent state verification."""
        now = datetime.now(timezone.utc)
        eval_log = [{
            "timestamp": now.isoformat(),
            "status": "initialized",
            "message": "Alert registered and pending next mandi session evaluation."
        }]

        alert = PriceAlert(
            alert_id=alert_id,
            query_id=query_id,
            crop=crop.capitalize(),
            market=market,
            target_price=target_price,
            unit=unit,
            threshold_direction=threshold_direction,
            status="active",
            is_simulated=True,
            created_at=now,
            evaluation_history=json.dumps(eval_log),
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)

        # Independent verification check
        persisted = db.query(PriceAlert).filter(PriceAlert.alert_id == alert_id).first()
        if not persisted or persisted.status != "active":
            return {
                "verified": False,
                "error": f"Verification failed: Alert {alert_id} not found in active state."
            }

        return {
            "verified": True,
            "alert_id": alert.alert_id,
            "crop": alert.crop,
            "market": alert.market,
            "target_price": alert.target_price,
            "unit": alert.unit,
            "threshold_direction": alert.threshold_direction,
            "status": alert.status,
            "is_simulated": alert.is_simulated,
            "verification_status": "verified_success",
            "message": f"Price alert for {alert.crop} at {alert.market} successfully created and verified active.",
        }

    @staticmethod
    def evaluate_alerts_against_records(
        db: Session,
        records: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Simulate evaluation of active alerts against new market arrivals."""
        active_alerts = db.query(PriceAlert).filter(PriceAlert.status == "active").all()
        results = []
        now = datetime.now(timezone.utc)

        for alert in active_alerts:
            # Match record by crop and market
            for r in records:
                if (
                    r.get("crop", "").lower() == alert.crop.lower()
                    and alert.market.lower() in r.get("market_name", "").lower()
                ):
                    modal_price = r.get("normalized_modal_price_per_kg")
                    if modal_price is None:
                        continue

                    triggered = False
                    if alert.threshold_direction == "below" and modal_price <= alert.target_price:
                        triggered = True
                    elif alert.threshold_direction == "above" and modal_price >= alert.target_price:
                        triggered = True

                    if triggered:
                        alert.status = "triggered"
                        alert.triggered_at = now
                        history = json.loads(alert.evaluation_history or "[]")
                        history.append({
                            "timestamp": now.isoformat(),
                            "status": "triggered",
                            "evaluated_price": modal_price,
                            "target_price": alert.target_price,
                            "message": (
                                f"[Simulated Alert] Price for {alert.crop} at {r.get('market_name')} "
                                f"hit ₹{modal_price:.2f}/kg ({alert.threshold_direction} target of ₹{alert.target_price:.2f})"
                            )
                        })
                        alert.evaluation_history = json.dumps(history)
                        db.commit()
                        results.append({
                            "alert_id": alert.alert_id,
                            "crop": alert.crop,
                            "market": alert.market,
                            "triggered_price": modal_price,
                        })
        return results
