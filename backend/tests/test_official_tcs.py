"""Automated test execution for the four mandatory hackathon test cases."""

import pytest
from backend.app.services.test_runner import OfficialTestCaseRunner


def test_official_tc1():
    result = OfficialTestCaseRunner.run_tc1()
    assert result["status"] == "passed"
    assert result["test_case_id"] == "TC1"
    assert len(result["assertions_failed"]) == 0
    assert result["actual_output"]["usable_count"] == 3
    assert result["actual_output"]["lowest_price"] == 20.0
    assert result["actual_output"]["highest_price"] == 24.0


def test_official_tc2():
    result = OfficialTestCaseRunner.run_tc2()
    assert result["status"] == "passed"
    assert result["test_case_id"] == "TC2"
    assert len(result["assertions_failed"]) == 0
    assert "yesterday's data" in result["actual_output"]["voice_answer_en"].lower()


def test_official_tc3():
    result = OfficialTestCaseRunner.run_tc3()
    assert result["status"] == "passed"
    assert result["test_case_id"] == "TC3"
    assert len(result["assertions_failed"]) == 0
    assert len(result["assertions_passed"]) == 4


def test_official_tc4():
    result = OfficialTestCaseRunner.run_tc4()
    assert result["status"] == "passed"
    assert result["test_case_id"] == "TC4"
    assert len(result["assertions_failed"]) == 0
    assert result["actual_output"]["scenario_1_calculable"] is False
    assert result["actual_output"]["scenario_2_net_proceeds"] == 24600.0
