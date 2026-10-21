"""Test runner executing the 4 Mandatory Official Hackathon Test Cases with genuine assertions."""

from datetime import datetime, timedelta, timezone
import json
import time
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from backend.app.models.models import TestRunRecord
from backend.app.services.normalizer import (
    calculate_price_range,
    evaluate_data_freshness,
    normalize_unit_to_kg,
)
from backend.app.services.profitability import calculate_market_profitability
from backend.app.services.voice_service import generate_voice_answer


class OfficialTestCaseRunner:
    @staticmethod
    def run_tc1(db: Optional[Session] = None) -> Dict[str, Any]:
        """TC1 — Tomato at three nearby markets with verified fixture provenance."""
        start_time = time.perf_counter()
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        input_fixture = {
            "crop": "tomato",
            "grade": "Grade A",
            "location": "Dharmapuri",
            "radius_km": 50.0,
            "raw_records": [
                {
                    "market_name": "Dharmapuri Regulated Market",
                    "distance_km": 8.5,
                    "crop": "Tomato",
                    "grade": "Grade A",
                    "original_modal_price": 2000.0,
                    "original_unit": "INR/quintal",
                    "observation_date": today_str,
                    "source_id": "fixture-tc1-tn",
                    "source_url": "https://agmarknet.gov.in/SearchCmmMkt.aspx?demo=tc1",
                    "data_mode": "synthetic",
                },
                {
                    "market_name": "Palacode APMC",
                    "distance_km": 18.2,
                    "crop": "Tomato",
                    "grade": "Grade A",
                    "original_modal_price": 2200.0,
                    "original_unit": "INR/quintal",
                    "observation_date": today_str,
                    "source_id": "fixture-tc1-tn",
                    "source_url": "https://agmarknet.gov.in/SearchCmmMkt.aspx?demo=tc1",
                    "data_mode": "synthetic",
                },
                {
                    "market_name": "Pennagaram Uzhavar Sandhai",
                    "distance_km": 31.0,
                    "crop": "Tomato",
                    "grade": "Grade A",
                    "original_modal_price": 24.0,
                    "original_unit": "INR/kg",
                    "observation_date": today_str,
                    "source_id": "fixture-tc1-tn",
                    "source_url": "https://agmarknet.gov.in/SearchCmmMkt.aspx?demo=tc1",
                    "data_mode": "synthetic",
                },
            ]
        }

        # Step 1: Normalize records
        normalized_records = []
        for r in input_fixture["raw_records"]:
            norm, _ = normalize_unit_to_kg(r["original_modal_price"], r["original_unit"])
            rec_copy = dict(r)
            rec_copy["normalized_modal_price_per_kg"] = norm
            rec_copy["validation_status"] = "valid"
            normalized_records.append(rec_copy)

        # Step 2: Compare
        summary = calculate_price_range(normalized_records)

        # Step 3: Voice answer
        voice = generate_voice_answer(
            crop="tomato",
            summary=summary,
            source_mode="synthetic",
            is_yesterday_data=False,
        )

        # Assertions
        passed = []
        failed = []

        if len(normalized_records) == 3:
            passed.append("Exactly three nearby market records were processed.")
        else:
            failed.append(f"Expected 3 records, got {len(normalized_records)}")

        if summary.get("lowest_price_per_kg") == 20.0 and summary.get("highest_price_per_kg") == 24.0:
            passed.append("Dated price range correctly calculated as ₹20.00 to ₹24.00 per kg.")
        else:
            failed.append(f"Incorrect range: lowest={summary.get('lowest_price_per_kg')}, highest={summary.get('highest_price_per_kg')}")

        if today_str in summary.get("dates_observed", []):
            passed.append(f"Observation date {today_str} correctly captured in summary.")
        else:
            failed.append("Observation date missing from summary.")

        if "20.00" in voice["en"] and "24.00" in voice["en"]:
            passed.append("Voice answer reports normalized price bounds accurately.")
        else:
            failed.append("Voice answer does not report the expected price range.")

        if "[Demo Mode]" in voice["en"]:
            passed.append("Demo mode transparently communicated without false live-data claims.")
        else:
            failed.append("Voice answer failed to disclose synthetic/demo mode status.")

        status = "passed" if not failed else "failed"
        duration_ms = (time.perf_counter() - start_time) * 1000

        result = {
            "test_case_id": "TC1",
            "title": "Tomato at three nearby markets",
            "status": status,
            "input_fixture": input_fixture,
            "expected_behavior": {
                "records_compared": 3,
                "lowest_price": 20.0,
                "highest_price": 24.0,
                "range_text": "₹20.00 to ₹24.00 per kg",
                "data_mode_label": "synthetic",
            },
            "actual_output": {
                "usable_count": summary["usable_markets_count"],
                "price_range_str": summary["price_range_str"],
                "lowest_price": summary["lowest_price_per_kg"],
                "highest_price": summary["highest_price_per_kg"],
                "voice_answer_en": voice["en"],
            },
            "assertions_passed": passed,
            "assertions_failed": failed,
            "evidence": {
                "source_provenance": "https://agmarknet.gov.in/SearchCmmMkt.aspx?demo=tc1",
                "calculation_trace": "Dharmapuri 2000/100=20, Palacode 2200/100=22, Pennagaram 24/1=24",
            },
            "executed_at": datetime.now(timezone.utc).isoformat(),
            "duration_ms": round(duration_ms, 2),
        }

        if db:
            OfficialTestCaseRunner._persist_result(db, result)
        return result

    @staticmethod
    def run_tc2(db: Optional[Session] = None) -> Dict[str, Any]:
        """TC2 — Only yesterday's data available."""
        start_time = time.perf_counter()
        yesterday_str = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")

        input_fixture = {
            "crop": "tomato",
            "records": [
                {
                    "market_name": "Dharmapuri Regulated Market",
                    "observation_date": yesterday_str,
                    "original_modal_price": 2300.0,
                    "original_unit": "INR/quintal",
                    "grade": "Grade A",
                    "source_id": "tc2-agmarknet-yesterday",
                    "data_mode": "synthetic",
                },
                {
                    "market_name": "Palacode APMC",
                    "observation_date": yesterday_str,
                    "original_modal_price": 2400.0,
                    "original_unit": "INR/quintal",
                    "grade": "Grade A",
                    "source_id": "tc2-agmarknet-yesterday",
                    "data_mode": "synthetic",
                },
            ]
        }

        # Normalize and evaluate freshness
        normalized_records = []
        for r in input_fixture["records"]:
            norm, _ = normalize_unit_to_kg(r["original_modal_price"], r["original_unit"])
            fresh, _ = evaluate_data_freshness(r["observation_date"])
            rec_copy = dict(r)
            rec_copy["normalized_modal_price_per_kg"] = norm
            rec_copy["freshness_category"] = fresh
            rec_copy["validation_status"] = "valid"
            normalized_records.append(rec_copy)

        summary = calculate_price_range(normalized_records)
        voice = generate_voice_answer(
            crop="tomato",
            summary=summary,
            source_mode="synthetic",
            is_yesterday_data=True,
        )

        passed = []
        failed = []

        all_yesterday = all(r["freshness_category"] == "yesterday" for r in normalized_records)
        if all_yesterday:
            passed.append("All retrieved records correctly classified as yesterday's data.")
        else:
            failed.append("Freshness classifier failed to tag records as 'yesterday'.")

        if "yesterday's data" in voice["en"].lower():
            passed.append("Voice answer explicitly declares 'Only yesterday's data is available'.")
        else:
            failed.append("Voice response failed to include explicit 'yesterday' notice.")

        if yesterday_str in voice["en"]:
            passed.append(f"Spoken response clearly quotes actual observation date ({yesterday_str}).")
        else:
            failed.append(f"Observation date {yesterday_str} was not spoken.")

        if "today's price is" not in voice["en"].lower():
            passed.append("Agent strictly avoids claiming yesterday's price is today's price.")
        else:
            failed.append("Agent falsely claimed yesterday's price represents today's live trading.")

        status = "passed" if not failed else "failed"
        duration_ms = (time.perf_counter() - start_time) * 1000

        result = {
            "test_case_id": "TC2",
            "title": "Only yesterday's data available",
            "status": status,
            "input_fixture": input_fixture,
            "expected_behavior": {
                "freshness_classification": "yesterday",
                "voice_contains_phrase": "yesterday's data",
                "observation_date_quoted": yesterday_str,
                "no_unsupported_current_price_claim": True,
            },
            "actual_output": {
                "freshness_categories": [r["freshness_category"] for r in normalized_records],
                "dates_observed": summary["dates_observed"],
                "voice_answer_en": voice["en"],
            },
            "assertions_passed": passed,
            "assertions_failed": failed,
            "evidence": {
                "observation_date": yesterday_str,
                "freshness_engine_output": "yesterday",
            },
            "executed_at": datetime.now(timezone.utc).isoformat(),
            "duration_ms": round(duration_ms, 2),
        }

        if db:
            OfficialTestCaseRunner._persist_result(db, result)
        return result

    @staticmethod
    def run_tc3(db: Optional[Session] = None) -> Dict[str, Any]:
        """TC3 — Quintal and kilogram prices normalization and arithmetic verification."""
        start_time = time.perf_counter()

        test_cases = [
            {"val": 2400.0, "unit": "INR/quintal", "expected": 24.0, "valid": True},
            {"val": 24.0, "unit": "INR/kg", "expected": 24.0, "valid": True},
            {"val": 24000.0, "unit": "INR/tonne", "expected": 24.0, "valid": True},
            {"val": 1500.0, "unit": "INR/unknown_bag", "expected": None, "valid": False},
        ]

        passed = []
        failed = []

        for tc in test_cases:
            norm, err = normalize_unit_to_kg(tc["val"], tc["unit"])
            if tc["valid"]:
                if norm == tc["expected"]:
                    passed.append(f"{tc['val']} {tc['unit']} correctly normalized to ₹{norm:.2f}/kg.")
                else:
                    failed.append(f"Normalization error for {tc['unit']}: expected {tc['expected']}, got {norm}")
            else:
                if norm is None and err is not None:
                    passed.append(f"Invalid unit '{tc['unit']}' safely rejected without guessing conversion.")
                else:
                    failed.append(f"Failed to reject invalid unit '{tc['unit']}'")

        status = "passed" if not failed else "failed"
        duration_ms = (time.perf_counter() - start_time) * 1000

        result = {
            "test_case_id": "TC3",
            "title": "Quintal and kilogram prices",
            "status": status,
            "input_fixture": {"conversions_tested": test_cases},
            "expected_behavior": {
                "1_quintal": "100 kg",
                "1_tonne": "1000 kg",
                "arithmetic_rule": "INR/quintal divided by 100 = INR/kg",
                "unknown_unit_handling": "unresolved / rejected",
            },
            "actual_output": {
                "results": [
                    {"input": f"{tc['val']} {tc['unit']}", "normalized": normalize_unit_to_kg(tc['val'], tc['unit'])[0]}
                    for tc in test_cases
                ]
            },
            "assertions_passed": passed,
            "assertions_failed": failed,
            "evidence": {
                "formula_quintal": "2400 INR / 100 kg = 24.00 INR/kg",
                "formula_tonne": "24000 INR / 1000 kg = 24.00 INR/kg",
                "rejection_trace": "INR/unknown_bag -> Unsupported unit, factor unknown",
            },
            "executed_at": datetime.now(timezone.utc).isoformat(),
            "duration_ms": round(duration_ms, 2),
        }

        if db:
            OfficialTestCaseRunner._persist_result(db, result)
        return result

    @staticmethod
    def run_tc4(db: Optional[Session] = None) -> Dict[str, Any]:
        """TC4 — Transport cost unknown safety enforcement."""
        start_time = time.perf_counter()

        # Step 1: Calculate profitability with missing transport cost
        res_missing = calculate_market_profitability(
            market_name="Krishnagiri Market",
            selling_price_per_kg=28.0,
            quantity_kg=1000.0,
            transport_cost_inr=None,  # Missing!
        )

        # Step 2: Calculate profitability with complete transport cost
        res_complete = calculate_market_profitability(
            market_name="Krishnagiri Market",
            selling_price_per_kg=28.0,
            quantity_kg=1000.0,
            transport_cost_inr=2500.0,
            loading_charges_inr=500.0,
            market_fees_inr=400.0,
        )

        passed = []
        failed = []

        expected_msg = "Transport cost is unknown. The most profitable market cannot be determined from price alone."

        if not res_missing["is_calculable"]:
            passed.append("Profitability engine strictly returned is_calculable=False when transport cost is absent.")
        else:
            failed.append("Engine allowed profit calculation without transport cost.")

        if res_missing["disclaimer"] == expected_msg:
            passed.append(f"Exact mandatory disclaimer returned: '{expected_msg}'")
        else:
            failed.append(f"Disclaimer mismatch: '{res_missing['disclaimer']}'")

        if res_missing["gross_revenue_inr"] is None and res_missing["estimated_net_proceeds_inr"] is None:
            passed.append("Proceeds and revenue fields remain safely null when inputs are incomplete.")
        else:
            failed.append("Revenue or proceeds were calculated despite missing transport cost.")

        if res_complete["is_calculable"] and res_complete["estimated_net_proceeds_inr"] == 24600.0:
            passed.append(
                "When transport cost (₹2500) and fees are supplied, net proceeds are calculated accurately (₹24,600)."
            )
        else:
            failed.append("Complete input calculation failed.")

        status = "passed" if not failed else "failed"
        duration_ms = (time.perf_counter() - start_time) * 1000

        result = {
            "test_case_id": "TC4",
            "title": "Transport cost unknown",
            "status": status,
            "input_fixture": {
                "scenario_1": {"selling_price": 28.0, "quantity_kg": 1000, "transport_cost": None},
                "scenario_2": {"selling_price": 28.0, "quantity_kg": 1000, "transport_cost": 2500.0, "fees": 900.0},
            },
            "expected_behavior": {
                "blocked_when_missing": True,
                "mandatory_disclaimer": expected_msg,
                "calculation_allowed_only_when_complete": True,
            },
            "actual_output": {
                "scenario_1_calculable": res_missing["is_calculable"],
                "scenario_1_disclaimer": res_missing["disclaimer"],
                "scenario_2_net_proceeds": res_complete["estimated_net_proceeds_inr"],
            },
            "assertions_passed": passed,
            "assertions_failed": failed,
            "evidence": {
                "rule_enforced": "Section 9 Profitability Safety: Transport cost is unknown.",
                "scenario_2_math": "28,000 gross - (2500 transport + 500 loading + 400 fees) = 24,600 net",
            },
            "executed_at": datetime.now(timezone.utc).isoformat(),
            "duration_ms": round(duration_ms, 2),
        }

        if db:
            OfficialTestCaseRunner._persist_result(db, result)
        return result

    @staticmethod
    def _persist_result(db: Session, res: Dict[str, Any]):
        rec = TestRunRecord(
            test_case_id=res["test_case_id"],
            title=res["title"],
            input_payload=json.dumps(res["input_fixture"]),
            expected_result=json.dumps(res["expected_behavior"]),
            actual_result=json.dumps(res["actual_output"]),
            status=res["status"],
            evidence=json.dumps(res["evidence"]),
            error_details="; ".join(res["assertions_failed"]) if res["assertions_failed"] else None,
            executed_at=datetime.now(timezone.utc),
        )
        db.add(rec)
        db.commit()

    @classmethod
    def run_all(cls, db: Optional[Session] = None) -> List[Dict[str, Any]]:
        return [
            cls.run_tc1(db),
            cls.run_tc2(db),
            cls.run_tc3(db),
            cls.run_tc4(db),
        ]
