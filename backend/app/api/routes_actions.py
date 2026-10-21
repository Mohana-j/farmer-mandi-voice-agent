"""Human-in-the-loop action approval, idempotency, and execution endpoints."""

from datetime import datetime, timezone
import json
import uuid
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.models import ActionRecord, MarketRecord
from backend.app.schemas.schemas import (
    ActionDecisionRequest,
    ActionExecutionResponse,
    ActionPreviewRequest,
    ActionPreviewResponse,
)
from backend.app.services.alert_service import AlertService
from backend.app.services.export_service import ExportService

router = APIRouter(prefix="/actions", tags=["Human-in-the-Loop Actions"])


@router.post("/preview", response_model=ActionPreviewResponse)
def create_action_preview(payload: ActionPreviewRequest, db: Session = Depends(get_db)):
    """Prepare a human-readable action preview with idempotency key before execution."""
    action_id = f"act-{uuid.uuid4().hex[:8]}"
    idempotency_key = f"idem-{payload.query_id}-{payload.action_type}-{uuid.uuid4().hex[:6]}"

    if payload.action_type == "export_comparison":
        records = db.query(MarketRecord).filter(MarketRecord.query_id == payload.query_id).all()
        if not records:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot export: No market records found for query '{payload.query_id}'"
            )
        preview_data = ExportService.prepare_export_preview(payload.query_id, records)
        destination = preview_data["destination_path"]
        summary = f"Export {preview_data['total_records']} verified market records to CSV ({preview_data['filename']})."

    elif payload.action_type == "create_price_alert":
        p = payload.payload
        crop = p.get("crop", "Tomato")
        market = p.get("market", "Dharmapuri Regulated Market")
        target_price = float(p.get("target_price", 22.0))
        unit = p.get("unit", "INR/kg")
        threshold_direction = p.get("threshold_direction", "below")

        preview_data = AlertService.prepare_alert_preview(
            crop=crop,
            market=market,
            target_price=target_price,
            unit=unit,
            threshold_direction=threshold_direction,
            query_id=payload.query_id,
        )
        destination = f"Simulated In-App Push ({market} - {crop})"
        summary = preview_data["summary_of_changes"]

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported action_type '{payload.action_type}'. Supported: 'export_comparison', 'create_price_alert'"
        )

    # Persist pending action in database
    action_rec = ActionRecord(
        action_id=action_id,
        query_id=payload.query_id,
        action_type=payload.action_type,
        action_payload=json.dumps(preview_data),
        action_version=1,
        idempotency_key=idempotency_key,
        approval_status="pending",
        execution_status="not_executed",
        verification_status="unverified",
    )
    db.add(action_rec)
    db.commit()

    return ActionPreviewResponse(
        action_id=action_id,
        query_id=payload.query_id,
        action_type=payload.action_type,
        action_version=1,
        idempotency_key=idempotency_key,
        destination=destination,
        summary_of_changes=summary,
        preview_data=preview_data,
        approval_status="pending",
    )


@router.post("/{action_id}/approve", response_model=ActionExecutionResponse)
def approve_and_execute_action(
    action_id: str,
    payload: ActionDecisionRequest,
    db: Session = Depends(get_db),
):
    """Explicitly approve and execute action exactly once with idempotency guard."""
    action = db.query(ActionRecord).filter(ActionRecord.action_id == action_id).first()
    if not action:
        raise HTTPException(status_code=404, detail=f"Action '{action_id}' not found")

    # Idempotency check: if already executed, return existing verified state without duplicating
    if action.execution_status == "completed":
        details = json.loads(action.verification_details or "{}")
        return ActionExecutionResponse(
            action_id=action.action_id,
            idempotency_key=action.idempotency_key,
            approval_status=action.approval_status,
            execution_status=action.execution_status,
            verification_status=action.verification_status,
            verification_details=details,
            message="Action was previously executed and verified (Idempotent response).",
        )

    if action.approval_status == "rejected":
        raise HTTPException(
            status_code=400,
            detail=f"Action '{action_id}' was already rejected and cannot be approved."
        )

    # Check idempotency key matches
    if action.idempotency_key != payload.idempotency_key:
        raise HTTPException(
            status_code=400,
            detail="Idempotency key mismatch. Potential replay attack or outdated action version."
        )

    now = datetime.now(timezone.utc)
    action.approval_status = "approved"
    action.approved_at = now
    stored_payload = json.loads(action.action_payload)

    verification_result: Dict[str, Any] = {}

    try:
        if action.action_type == "export_comparison":
            records = db.query(MarketRecord).filter(MarketRecord.query_id == action.query_id).all()
            export_id = f"exp-{uuid.uuid4().hex[:6]}"
            filename = stored_payload["filename"]
            verification_result = ExportService.execute_and_verify_export(
                db=db,
                query_id=action.query_id,
                export_id=export_id,
                filename=filename,
                records=records,
            )

        elif action.action_type == "create_price_alert":
            alert_id = f"alt-{uuid.uuid4().hex[:6]}"
            verification_result = AlertService.execute_and_verify_alert(
                db=db,
                alert_id=alert_id,
                crop=stored_payload["crop"],
                market=stored_payload["market"],
                target_price=stored_payload["target_price"],
                unit=stored_payload.get("unit", "INR/kg"),
                threshold_direction=stored_payload.get("threshold_direction", "below"),
                query_id=action.query_id,
            )

        # Update action execution status
        action.executed_at = now
        action.execution_status = "completed"
        action.verification_status = "verified_success" if verification_result.get("verified") else "verification_failed"
        action.verification_details = json.dumps(verification_result)
        db.commit()

        return ActionExecutionResponse(
            action_id=action.action_id,
            idempotency_key=action.idempotency_key,
            approval_status=action.approval_status,
            execution_status=action.execution_status,
            verification_status=action.verification_status,
            verification_details=verification_result,
            message=verification_result.get("message", "Action executed and verified successfully."),
        )

    except Exception as exc:
        action.executed_at = now
        action.execution_status = "failed"
        action.verification_status = "verification_failed"
        action.verification_details = json.dumps({"error": str(exc)})
        db.commit()
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(exc)}")


@router.post("/{action_id}/reject", response_model=ActionExecutionResponse)
def reject_action(action_id: str, db: Session = Depends(get_db)):
    """Reject an action, ensuring it remains unexecuted."""
    action = db.query(ActionRecord).filter(ActionRecord.action_id == action_id).first()
    if not action:
        raise HTTPException(status_code=404, detail=f"Action '{action_id}' not found")

    if action.execution_status == "completed":
        raise HTTPException(status_code=400, detail="Cannot reject an action that has already been executed.")

    action.approval_status = "rejected"
    action.execution_status = "not_executed"
    action.verification_status = "unverified"
    db.commit()

    return ActionExecutionResponse(
        action_id=action.action_id,
        idempotency_key=action.idempotency_key,
        approval_status="rejected",
        execution_status="not_executed",
        verification_status="unverified",
        verification_details={"status": "rejected_by_user"},
        message=f"Action '{action_id}' has been rejected and will not be executed.",
    )


@router.get("/{action_id}")
def get_action_status(action_id: str, db: Session = Depends(get_db)):
    """Inspect stored action record and audit status."""
    action = db.query(ActionRecord).filter(ActionRecord.action_id == action_id).first()
    if not action:
        raise HTTPException(status_code=404, detail=f"Action '{action_id}' not found")

    return {
        "action_id": action.action_id,
        "query_id": action.query_id,
        "action_type": action.action_type,
        "action_version": action.action_version,
        "idempotency_key": action.idempotency_key,
        "approval_status": action.approval_status,
        "approved_at": action.approved_at,
        "executed_at": action.executed_at,
        "execution_status": action.execution_status,
        "verification_status": action.verification_status,
        "verification_details": json.loads(action.verification_details or "{}"),
    }
