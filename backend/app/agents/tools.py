"""Explicit agent tools for the Farmer Mandi Price Voice Agent."""

import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

from backend.app.agents.state import AgentState
from backend.app.services.gemini_adapter import GeminiAdapter
from backend.app.services.market_adapter import MarketDataAdapter
from backend.app.services.normalizer import (
    assess_grade_compatibility,
    calculate_price_range,
    evaluate_data_freshness,
    normalize_unit_to_kg,
)
from backend.app.services.voice_service import generate_voice_answer


class AgentTools:
    def __init__(self):
        self.gemini = GeminiAdapter()
        self.market_adapter = MarketDataAdapter()

    async def parse_query(self, state: AgentState) -> AgentState:
        """Tool 1: parse_farmer_query"""
        start = time.perf_counter()
        if state.raw_transcript and (not state.input_crop or not state.input_location):
            parsed = await self.gemini.parse_farmer_query(state.raw_transcript)
            state.crop = state.input_crop or parsed.get("crop", "tomato")
            state.grade = state.input_grade or parsed.get("grade", "Grade A")
            state.location = state.input_location or parsed.get("location", "Dharmapuri")
            state.radius_km = state.input_radius_km or parsed.get("radius_km", 50.0)
            state.language = state.input_language or parsed.get("language", "en")
            out_info = {"parsed_by": parsed.get("engine", "rule-engine"), "result": parsed}
        else:
            state.crop = state.input_crop or "tomato"
            state.grade = state.input_grade or "Grade A"
            state.location = state.input_location or "Dharmapuri"
            state.radius_km = state.input_radius_km or 50.0
            state.language = state.input_language or "en"
            out_info = {"method": "direct_input", "crop": state.crop, "location": state.location}

        duration = (time.perf_counter() - start) * 1000
        state.tool_events.append({
            "tool": "parse_farmer_query",
            "inputs": {"raw_transcript": state.raw_transcript},
            "outputs": out_info,
            "duration_ms": round(duration, 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        return state

    def validate_query(self, state: AgentState) -> AgentState:
        """Tool 2: validate_query"""
        start = time.perf_counter()
        errors = []

        if not state.crop or not state.crop.strip():
            errors.append("Crop is required (e.g. Tomato, Onion).")
        if not state.location or not state.location.strip():
            errors.append("Location is required. Please provide a village, town, or district.")
        if state.radius_km <= 0 or state.radius_km > 500:
            errors.append("Radius must be between 1 km and 500 km.")

        if errors:
            state.validation_passed = False
            state.clarification_needed = True
            state.clarification_message = " ".join(errors)
        else:
            state.validation_passed = True
            state.clarification_needed = False

        duration = (time.perf_counter() - start) * 1000
        state.tool_events.append({
            "tool": "validate_query",
            "inputs": {"crop": state.crop, "location": state.location, "radius_km": state.radius_km},
            "outputs": {"valid": state.validation_passed, "errors": errors},
            "duration_ms": round(duration, 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        return state

    async def discover_and_fetch_sources(self, state: AgentState) -> AgentState:
        """Tool 3 & 4: discover_market_sources and fetch_market_records"""
        start = time.perf_counter()
        adapter = MarketDataAdapter(mode=state.source_mode)

        records, active_mode, metadata = await adapter.fetch_market_records(
            crop=state.crop,
            location=state.location,
            radius_km=state.radius_km,
        )

        state.source_mode = active_mode
        state.selected_source = metadata.get("source_endpoint") or "Agmarknet Public Fixtures"
        state.raw_retrieved_records = records

        duration = (time.perf_counter() - start) * 1000
        state.tool_events.append({
            "tool": "fetch_market_records",
            "inputs": {"crop": state.crop, "location": state.location, "mode": state.source_mode},
            "outputs": {
                "active_mode": active_mode,
                "records_retrieved": len(records),
                "metadata": metadata,
            },
            "duration_ms": round(duration, 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        return state

    def normalize_and_validate_records(self, state: AgentState) -> AgentState:
        """Tool 5, 6, 7: normalize_price_units, assess_grade_compatibility, evaluate_data_freshness"""
        start = time.perf_counter()
        normalized_list = []
        usable_list = []
        excluded_list = []

        yesterday_count = 0
        total_valid = 0

        for r in state.raw_retrieved_records:
            item = dict(r)
            # 1. Unit conversion
            norm_modal, err_modal = normalize_unit_to_kg(item.get("original_modal_price"), item.get("original_unit", ""))
            norm_min, _ = normalize_unit_to_kg(item.get("original_price_min"), item.get("original_unit", ""))
            norm_max, _ = normalize_unit_to_kg(item.get("original_price_max"), item.get("original_unit", ""))

            item["normalized_modal_price_per_kg"] = norm_modal
            item["normalized_price_min_per_kg"] = norm_min
            item["normalized_price_max_per_kg"] = norm_max

            # 2. Grade compatibility
            compatible, grade_msg = assess_grade_compatibility(state.grade, item.get("grade", "unknown"))

            # 3. Data freshness
            freshness, fresh_msg = evaluate_data_freshness(item.get("observation_date", ""))
            item["freshness_category"] = freshness

            # 4. Location / radius filter (if distance is trustworthy)
            dist = item.get("distance_km")
            distance_ok = True
            if dist is not None and dist > state.radius_km:
                distance_ok = False

            # Determine validation status
            if norm_modal is None and norm_min is None and norm_max is None:
                item["validation_status"] = "unknown_unit"
                item["exclusion_reason"] = f"Unit '{item.get('original_unit')}' cannot be safely converted."
                excluded_list.append(item)
            elif not compatible:
                item["validation_status"] = "incompatible_grade"
                item["exclusion_reason"] = grade_msg
                excluded_list.append(item)
            elif not distance_ok:
                item["validation_status"] = "outside_radius"
                item["exclusion_reason"] = f"Distance {dist} km exceeds specified radius of {state.radius_km} km."
                excluded_list.append(item)
            else:
                if "Provisional" in grade_msg:
                    item["validation_status"] = "provisional"
                else:
                    item["validation_status"] = "valid"
                usable_list.append(item)
                total_valid += 1
                if freshness == "yesterday":
                    yesterday_count += 1

            normalized_list.append(item)

        state.normalized_records = normalized_list
        state.usable_records = usable_list
        state.excluded_records = excluded_list
        state.is_yesterday_data = (total_valid > 0 and yesterday_count == total_valid)

        duration = (time.perf_counter() - start) * 1000
        state.tool_events.append({
            "tool": "normalize_and_validate_records",
            "inputs": {"records_count": len(state.raw_retrieved_records), "query_grade": state.grade},
            "outputs": {
                "usable_count": len(usable_list),
                "excluded_count": len(excluded_list),
                "is_yesterday_data": state.is_yesterday_data,
            },
            "duration_ms": round(duration, 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        return state

    def compare_and_summarize(self, state: AgentState) -> AgentState:
        """Tool 8: compare_market_records"""
        start = time.perf_counter()
        summary = calculate_price_range(state.usable_records)
        state.summary = summary

        duration = (time.perf_counter() - start) * 1000
        state.tool_events.append({
            "tool": "compare_market_records",
            "inputs": {"usable_records_count": len(state.usable_records)},
            "outputs": summary,
            "duration_ms": round(duration, 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        return state

    def generate_voice_answer(self, state: AgentState) -> AgentState:
        """Tool 9: generate_voice_answer"""
        start = time.perf_counter()
        answers = generate_voice_answer(
            crop=state.crop,
            summary=state.summary,
            source_mode=state.source_mode,
            is_yesterday_data=state.is_yesterday_data,
            is_stale_or_uncertain=(state.summary.get("usable_markets_count", 0) > 0 and "provisional" in state.summary.get("grade_compatibility_note", "").lower()),
        )
        state.voice_answer_en = answers["en"]
        state.voice_answer_ta = answers["ta"]

        duration = (time.perf_counter() - start) * 1000
        state.tool_events.append({
            "tool": "generate_voice_answer",
            "inputs": {"summary_range": state.summary.get("price_range_str")},
            "outputs": answers,
            "duration_ms": round(duration, 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        return state
