"""Agentic AI workflow orchestrator for Farmer Mandi Price Voice Agent."""

from datetime import datetime, timezone
import json
import logging
import uuid
from typing import Any, Dict
from sqlalchemy.orm import Session

from backend.app.agents.state import AgentState
from backend.app.agents.tools import AgentTools
from backend.app.models.models import AgentRun, FarmerQuery, MarketRecord

logger = logging.getLogger(__name__)


class MandiPriceAgentOrchestrator:
    def __init__(self, db: Session):
        self.db = db
        self.tools = AgentTools()

    async def execute_query_pipeline(
        self,
        query: FarmerQuery,
        execution_id: str,
    ) -> AgentState:
        """Execute full multi-step agent workflow."""
        now = datetime.now(timezone.utc)
        agent_run = AgentRun(
            query_id=query.query_id,
            execution_id=execution_id,
            current_state="initialized",
            tool_events="[]",
            planning_steps=json.dumps([
                "1. Parse voice transcript or form inputs",
                "2. Validate crop, grade, location, and radius constraints",
                "3. Discover authorized mandi price source (live portal vs synthetic mode)",
                "4. Fetch agricultural records with provenance tracking",
                "5. Deterministically normalize units (quintal/tonne to INR/kg)",
                "6. Verify grade compatibility and data freshness dates",
                "7. Compare nearby markets and compute dated price range",
                "8. Synthesize grounded voice response in English and Tamil",
                "9. Persist verified audit evidence into database"
            ]),
            started_at=now,
        )
        self.db.add(agent_run)
        self.db.commit()

        state = AgentState(
            query_id=query.query_id,
            execution_id=execution_id,
            source_mode=query.source_mode,
            raw_transcript=query.transcript,
            input_crop=query.crop,
            input_grade=query.grade,
            input_location=query.location,
            input_radius_km=query.radius_km,
            input_language=query.language,
        )

        try:
            # Step 1: Parse
            agent_run.current_state = "parsing_query"
            self.db.commit()
            state = await self.tools.parse_query(state)

            # Step 2: Validate
            agent_run.current_state = "validating_inputs"
            self.db.commit()
            state = self.tools.validate_query(state)

            if state.clarification_needed:
                query.status = "clarification_needed"
                query.clarification_message = state.clarification_message
                agent_run.current_state = "clarification_needed"
                agent_run.completed_at = datetime.now(timezone.utc)
                agent_run.tool_events = json.dumps(state.tool_events)
                self.db.commit()
                return state

            # Update query with validated parameters
            query.crop = state.crop
            query.grade = state.grade
            query.location = state.location
            query.radius_km = state.radius_km
            query.language = state.language
            self.db.commit()

            # Step 3 & 4: Fetch
            agent_run.current_state = "fetching_records"
            self.db.commit()
            state = await self.tools.discover_and_fetch_sources(state)

            # Step 5, 6, 7: Normalize, Grade, Freshness
            agent_run.current_state = "normalizing_data"
            self.db.commit()
            state = self.tools.normalize_and_validate_records(state)

            # Save market records to DB
            for item in state.normalized_records:
                m_rec = MarketRecord(
                    query_id=state.query_id,
                    source_id=item.get("source_id", "source"),
                    source_url=item.get("source_url", ""),
                    source_record_id=item.get("source_record_id", ""),
                    market_name=item.get("market_name", "Unknown Mandi"),
                    market_location=item.get("market_location", ""),
                    distance_km=item.get("distance_km"),
                    crop=item.get("crop", state.crop),
                    grade=item.get("grade", state.grade),
                    original_price_min=item.get("original_price_min"),
                    original_price_max=item.get("original_price_max"),
                    original_modal_price=item.get("original_modal_price"),
                    original_unit=item.get("original_unit", "INR/quintal"),
                    normalized_price_min_per_kg=item.get("normalized_price_min_per_kg"),
                    normalized_price_max_per_kg=item.get("normalized_price_max_per_kg"),
                    normalized_modal_price_per_kg=item.get("normalized_modal_price_per_kg"),
                    observation_date=item.get("observation_date", now.strftime("%Y-%m-%d")),
                    freshness_category=item.get("freshness_category", "today"),
                    retrieved_at=now,
                    data_mode=item.get("data_mode", state.source_mode),
                    validation_status=item.get("validation_status", "valid"),
                    exclusion_reason=item.get("exclusion_reason"),
                )
                self.db.add(m_rec)
            self.db.commit()

            # Step 8: Compare and summarize
            agent_run.current_state = "comparing_markets"
            self.db.commit()
            state = self.tools.compare_and_summarize(state)

            # Step 9: Generate voice response
            agent_run.current_state = "generating_voice_response"
            self.db.commit()
            state = self.tools.generate_voice_answer(state)

            # Finalize query record
            query.voice_response_en = state.voice_answer_en
            query.voice_response_ta = state.voice_answer_ta
            query.source_mode = state.source_mode
            query.status = "completed"

            # Finalize agent run
            agent_run.current_state = "completed"
            agent_run.completed_at = datetime.now(timezone.utc)
            agent_run.tool_events = json.dumps(state.tool_events)
            self.db.commit()

            return state

        except Exception as exc:
            logger.error(f"Agent pipeline encountered error: {exc}", exc_info=True)
            self.db.rollback()
            query.status = "failed"
            agent_run.current_state = "failed"
            agent_run.errors = str(exc)
            agent_run.completed_at = datetime.now(timezone.utc)
            agent_run.tool_events = json.dumps(state.tool_events)
            self.db.commit()
            raise exc
