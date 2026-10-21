"""SQLAlchemy database models for Farmer Mandi Price Voice Agent."""

from datetime import datetime, timezone
import json
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
)
from backend.app.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class FarmerQuery(Base):
    __tablename__ = "farmer_queries"

    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(String(64), unique=True, index=True, nullable=False)
    crop = Column(String(64), nullable=False, default="tomato")
    grade = Column(String(64), nullable=False, default="unknown")
    location = Column(String(128), nullable=False, default="Dharmapuri")
    radius_km = Column(Float, nullable=False, default=50.0)
    language = Column(String(10), nullable=False, default="en")  # 'en' or 'ta'
    transcript = Column(Text, nullable=True)
    source_mode = Column(String(20), nullable=False, default="synthetic")  # 'synthetic' or 'live'
    status = Column(String(32), nullable=False, default="pending")  # pending, completed, failed, clarification_needed
    voice_response_en = Column(Text, nullable=True)
    voice_response_ta = Column(Text, nullable=True)
    clarification_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)


class MarketRecord(Base):
    __tablename__ = "market_records"

    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(String(64), index=True, nullable=False)
    source_id = Column(String(64), nullable=False)
    source_url = Column(String(256), nullable=False)
    source_record_id = Column(String(64), nullable=False)
    market_name = Column(String(128), nullable=False)
    market_location = Column(String(128), nullable=False)
    distance_km = Column(Float, nullable=True)
    crop = Column(String(64), nullable=False)
    grade = Column(String(64), nullable=False, default="Grade A")
    original_price_min = Column(Float, nullable=True)
    original_price_max = Column(Float, nullable=True)
    original_modal_price = Column(Float, nullable=True)
    original_unit = Column(String(32), nullable=False)  # 'INR/quintal', 'INR/kg', etc.
    normalized_price_min_per_kg = Column(Float, nullable=True)
    normalized_price_max_per_kg = Column(Float, nullable=True)
    normalized_modal_price_per_kg = Column(Float, nullable=True)
    observation_date = Column(String(32), nullable=False)  # YYYY-MM-DD
    freshness_category = Column(String(32), nullable=False, default="today")  # today, yesterday, older, unknown
    retrieved_at = Column(DateTime, default=utc_now, nullable=False)
    data_mode = Column(String(20), nullable=False, default="synthetic")  # 'live' or 'synthetic'
    validation_status = Column(String(32), nullable=False, default="valid")  # valid, provisional, incompatible_grade, unknown_unit, stale
    exclusion_reason = Column(String(256), nullable=True)


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(String(64), index=True, nullable=False)
    execution_id = Column(String(64), unique=True, index=True, nullable=False)
    current_state = Column(String(64), nullable=False, default="initialized")
    tool_events = Column(Text, nullable=False, default="[]")  # JSON list
    planning_steps = Column(Text, nullable=False, default="[]")  # JSON list
    errors = Column(Text, nullable=True)  # JSON or string
    started_at = Column(DateTime, default=utc_now, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    def append_tool_event(self, tool_name: str, inputs: Any, outputs: Any, duration_ms: float = 0.0):
        try:
            events = json.loads(self.tool_events or "[]")
        except Exception:
            events = []
        events.append({
            "tool": tool_name,
            "inputs": inputs,
            "outputs": outputs,
            "duration_ms": duration_ms,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        self.tool_events = json.dumps(events)


class ActionRecord(Base):
    __tablename__ = "action_records"

    id = Column(Integer, primary_key=True, index=True)
    action_id = Column(String(64), unique=True, index=True, nullable=False)
    query_id = Column(String(64), index=True, nullable=False)
    action_type = Column(String(64), nullable=False)  # 'export_comparison', 'create_price_alert'
    action_payload = Column(Text, nullable=False)  # JSON dict of proposed changes
    action_version = Column(Integer, nullable=False, default=1)
    idempotency_key = Column(String(128), unique=True, index=True, nullable=False)
    approval_status = Column(String(32), nullable=False, default="pending")  # pending, approved, rejected
    approved_at = Column(DateTime, nullable=True)
    executed_at = Column(DateTime, nullable=True)
    execution_status = Column(String(32), nullable=False, default="not_executed")  # not_executed, completed, failed
    verification_status = Column(String(32), nullable=False, default="unverified")  # unverified, verified_success, verification_failed
    verification_details = Column(Text, nullable=True)  # JSON


class PriceAlert(Base):
    __tablename__ = "price_alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String(64), unique=True, index=True, nullable=False)
    query_id = Column(String(64), nullable=True)
    crop = Column(String(64), nullable=False)
    market = Column(String(128), nullable=False)
    target_price = Column(Float, nullable=False)
    unit = Column(String(32), nullable=False, default="INR/kg")
    threshold_direction = Column(String(16), nullable=False, default="below")  # 'above' or 'below'
    status = Column(String(32), nullable=False, default="active")  # active, triggered, paused, cancelled
    is_simulated = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    triggered_at = Column(DateTime, nullable=True)
    evaluation_history = Column(Text, nullable=False, default="[]")  # JSON


class ExportRecord(Base):
    __tablename__ = "export_records"

    id = Column(Integer, primary_key=True, index=True)
    export_id = Column(String(64), unique=True, index=True, nullable=False)
    query_id = Column(String(64), nullable=False)
    file_path = Column(String(256), nullable=False)
    filename = Column(String(128), nullable=False)
    row_count = Column(Integer, nullable=False, default=0)
    columns = Column(Text, nullable=False, default="[]")  # JSON
    verification_hash = Column(String(64), nullable=True)
    is_verified = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)


class TestRunRecord(Base):
    __tablename__ = "test_run_records"

    id = Column(Integer, primary_key=True, index=True)
    test_case_id = Column(String(16), nullable=False)  # TC1, TC2, TC3, TC4
    title = Column(String(128), nullable=False)
    input_payload = Column(Text, nullable=False)  # JSON
    expected_result = Column(Text, nullable=False)  # JSON
    actual_result = Column(Text, nullable=False)  # JSON
    status = Column(String(16), nullable=False)  # passed, failed
    evidence = Column(Text, nullable=False, default="{}")  # JSON
    error_details = Column(Text, nullable=True)
    executed_at = Column(DateTime, default=utc_now, nullable=False)
