"""State representations for the Agentic AI orchestrator."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AgentState(BaseModel):
    query_id: str
    execution_id: str
    current_step: str = "initialized"
    source_mode: str = "synthetic"  # 'synthetic' or 'live'

    # Raw inputs
    raw_transcript: Optional[str] = None
    input_crop: Optional[str] = None
    input_grade: Optional[str] = None
    input_location: Optional[str] = None
    input_radius_km: Optional[float] = None
    input_language: str = "en"

    # Parsed & validated query parameters
    crop: str = "tomato"
    grade: str = "Grade A"
    location: str = "Dharmapuri"
    radius_km: float = 50.0
    language: str = "en"
    validation_passed: bool = False
    clarification_needed: bool = False
    clarification_message: Optional[str] = None

    # Planning & Tool outputs
    planning_steps: List[str] = Field(default_factory=list)
    selected_source: Optional[str] = None
    raw_retrieved_records: List[Dict[str, Any]] = Field(default_factory=list)
    normalized_records: List[Dict[str, Any]] = Field(default_factory=list)
    usable_records: List[Dict[str, Any]] = Field(default_factory=list)
    excluded_records: List[Dict[str, Any]] = Field(default_factory=list)

    # Comparison & Summary
    summary: Dict[str, Any] = Field(default_factory=dict)
    is_yesterday_data: bool = False
    is_stale_or_uncertain: bool = False

    # Responses
    voice_answer_en: Optional[str] = None
    voice_answer_ta: Optional[str] = None

    # Actions & Auditing
    tool_events: List[Dict[str, Any]] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
