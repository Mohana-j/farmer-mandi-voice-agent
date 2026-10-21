"""Pydantic schemas for Farmer Mandi Price Voice Agent."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


# Query schemas
class FarmerQueryCreate(BaseModel):
    crop: str = Field(default="tomato", description="Agricultural commodity name")
    grade: str = Field(default="Grade A", description="Crop grade or 'unknown'")
    location: str = Field(default="Dharmapuri", description="Farmer reference location / market town")
    radius_km: float = Field(default=50.0, ge=1.0, le=500.0, description="Search radius in kilometers")
    language: str = Field(default="en", description="'en' for English, 'ta' for Tamil")
    transcript: Optional[str] = Field(default=None, description="Raw speech or text transcription")
    source_mode: Optional[str] = Field(default="synthetic", description="'synthetic' or 'live'")


class FarmerQueryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    query_id: str
    crop: str
    grade: str
    location: str
    radius_km: float
    language: str
    transcript: Optional[str]
    source_mode: str
    status: str
    voice_response_en: Optional[str]
    voice_response_ta: Optional[str]
    clarification_message: Optional[str]
    created_at: datetime
    updated_at: datetime


# Market record schemas
class MarketRecordSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    query_id: str
    source_id: str
    source_url: str
    source_record_id: str
    market_name: str
    market_location: str
    distance_km: Optional[float] = None
    crop: str
    grade: str
    original_price_min: Optional[float] = None
    original_price_max: Optional[float] = None
    original_modal_price: Optional[float] = None
    original_unit: str
    normalized_price_min_per_kg: Optional[float] = None
    normalized_price_max_per_kg: Optional[float] = None
    normalized_modal_price_per_kg: Optional[float] = None
    observation_date: str
    freshness_category: str  # 'today', 'yesterday', 'older', 'unknown'
    retrieved_at: datetime
    data_mode: str  # 'live' or 'synthetic'
    validation_status: str  # 'valid', 'provisional', 'incompatible_grade', 'unknown_unit', 'stale'
    exclusion_reason: Optional[str] = None


# Comparison summary
class ComparisonSummary(BaseModel):
    lowest_price_per_kg: Optional[float]
    highest_price_per_kg: Optional[float]
    price_range_str: str
    usable_markets_count: int
    excluded_markets_count: int
    all_same_date: bool
    dates_observed: List[str]
    freshness_summary: str
    grade_compatibility_note: str
    profitability_disclaimer: str
    source_names: List[str]


# Full query results
class QueryResultsResponse(BaseModel):
    query: FarmerQueryResponse
    records: List[MarketRecordSchema]
    summary: ComparisonSummary
    voice_answer_en: str
    voice_answer_ta: str
    execution_id: str
    source_mode: str


# Action preview & approval
class ActionPreviewRequest(BaseModel):
    query_id: str
    action_type: str = Field(..., description="'export_comparison' or 'create_price_alert'")
    payload: Dict[str, Any] = Field(default_factory=dict)


class ActionPreviewResponse(BaseModel):
    action_id: str
    query_id: str
    action_type: str
    action_version: int
    idempotency_key: str
    destination: str
    summary_of_changes: str
    preview_data: Dict[str, Any]
    approval_status: str


class ActionDecisionRequest(BaseModel):
    idempotency_key: str
    approved: bool


class ActionExecutionResponse(BaseModel):
    action_id: str
    idempotency_key: str
    approval_status: str
    execution_status: str
    verification_status: str
    verification_details: Optional[Dict[str, Any]] = None
    message: str


# Price Alert schemas
class PriceAlertCreate(BaseModel):
    query_id: Optional[str] = None
    crop: str
    market: str
    target_price: float
    unit: str = "INR/kg"
    threshold_direction: str = "below"  # 'above' or 'below'


class PriceAlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    alert_id: str
    query_id: Optional[str]
    crop: str
    market: str
    target_price: float
    unit: str
    threshold_direction: str
    status: str
    is_simulated: bool
    created_at: datetime
    triggered_at: Optional[datetime]
    evaluation_history: List[Dict[str, Any]]


# Profitability safety schemas
class ProfitabilityCalculationRequest(BaseModel):
    query_id: Optional[str] = None
    market_name: str
    selling_price_per_kg: float
    quantity_kg: float
    transport_cost_inr: Optional[float] = None
    loading_charges_inr: float = 0.0
    market_fees_inr: float = 0.0
    packaging_costs_inr: float = 0.0


class ProfitabilityCalculationResponse(BaseModel):
    is_calculable: bool
    market_name: str
    disclaimer: str
    gross_revenue_inr: Optional[float] = None
    total_estimated_costs_inr: Optional[float] = None
    estimated_net_proceeds_inr: Optional[float] = None
    cost_breakdown: Optional[Dict[str, float]] = None


# Evidence and Audit schemas
class AuditEvent(BaseModel):
    tool: str
    inputs: Any
    outputs: Any
    duration_ms: float
    timestamp: str


class AuditTrailResponse(BaseModel):
    query_id: str
    execution_id: str
    source_mode: str
    records_count: int
    tool_events: List[AuditEvent]
    planning_steps: List[str]
    normalization_decisions: List[Dict[str, Any]]
    actions_taken: List[Dict[str, Any]]
    verification_checks: List[Dict[str, Any]]


# Test case schemas
class TestCaseResult(BaseModel):
    test_case_id: str
    title: str
    status: str  # passed, failed
    input_fixture: Dict[str, Any]
    expected_behavior: Dict[str, Any]
    actual_output: Dict[str, Any]
    assertions_passed: List[str]
    assertions_failed: List[str]
    evidence: Dict[str, Any]
    executed_at: str
    duration_ms: float
