"""Tests for Human-in-the-Loop approval, idempotency, and post-execution verification."""

from datetime import datetime, timezone
import pytest
from sqlalchemy.orm import Session

from backend.app.models.models import ActionRecord, FarmerQuery, MarketRecord, PriceAlert
from backend.app.services.alert_service import AlertService
from backend.app.services.export_service import ExportService


def test_export_action_approval_and_verification(db_session: Session):
    query_id = "q-test-export-01"
    now = datetime.now(timezone.utc)

    # Setup dummy query & records
    query = FarmerQuery(query_id=query_id, crop="Tomato", location="Dharmapuri")
    db_session.add(query)

    rec = MarketRecord(
        query_id=query_id,
        source_id="test-source",
        source_url="https://test.mandi.gov.in",
        source_record_id="REC-01",
        market_name="Dharmapuri Regulated Market",
        market_location="Dharmapuri Town",
        crop="Tomato",
        grade="Grade A",
        original_price_min=18.0,
        original_price_max=22.0,
        original_modal_price=20.0,
        original_unit="INR/kg",
        normalized_modal_price_per_kg=20.0,
        observation_date=now.strftime("%Y-%m-%d"),
        freshness_category="today",
        retrieved_at=now,
        data_mode="synthetic",
        validation_status="valid",
    )
    db_session.add(rec)
    db_session.commit()

    records = [rec]

    # Step 1: Preview
    preview = ExportService.prepare_export_preview(query_id, records)
    assert preview["total_records"] == 1
    assert "mandi_comparison_q-test-export-01" in preview["filename"]

    # Step 2: Execute & verify
    verif = ExportService.execute_and_verify_export(
        db=db_session,
        query_id=query_id,
        export_id="exp-01",
        filename=preview["filename"],
        records=records,
    )
    assert verif["verified"] is True
    assert verif["verification_status"] == "verified_success"
    assert verif["rows_written"] == 1
    assert len(verif["sha256_hash"]) == 64


def test_price_alert_approval_and_verification(db_session: Session):
    alert_id = "alt-test-01"
    verif = AlertService.execute_and_verify_alert(
        db=db_session,
        alert_id=alert_id,
        crop="Tomato",
        market="Palacode APMC",
        target_price=20.0,
        unit="INR/kg",
        threshold_direction="below",
        query_id="q-test-alert",
    )
    assert verif["verified"] is True
    assert verif["status"] == "active"
    assert verif["is_simulated"] is True

    # Check alert exists in DB
    persisted = db_session.query(PriceAlert).filter(PriceAlert.alert_id == alert_id).first()
    assert persisted is not None
    assert persisted.status == "active"
