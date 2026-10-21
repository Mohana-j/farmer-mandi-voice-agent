"""Tests for unit conversion, grade compatibility, and range calculations."""

import pytest
from backend.app.services.normalizer import (
    assess_grade_compatibility,
    calculate_price_range,
    normalize_unit_to_kg,
)


def test_quintal_to_kg_normalization():
    # 2400 INR/quintal = 24.00 INR/kg
    val, err = normalize_unit_to_kg(2400.0, "INR/quintal")
    assert err is None
    assert val == 24.00

    val2, _ = normalize_unit_to_kg(1850.0, "Rs/Quintal")
    assert val2 == 18.50


def test_tonne_to_kg_normalization():
    # 24000 INR/tonne = 24.00 INR/kg
    val, err = normalize_unit_to_kg(24000.0, "INR/tonne")
    assert err is None
    assert val == 24.00


def test_kg_normalization():
    val, err = normalize_unit_to_kg(22.50, "INR/kg")
    assert err is None
    assert val == 22.50


def test_unknown_unit_rejection():
    # Never guess conversion factor for unknown unit
    val, err = normalize_unit_to_kg(500.0, "bags")
    assert val is None
    assert "Unsupported unit" in err


def test_null_price_handling():
    val, err = normalize_unit_to_kg(None, "INR/kg")
    assert val is None
    assert "absent or null" in err


def test_grade_compatibility():
    # Matching grades
    comp, msg = assess_grade_compatibility("Grade A", "Grade A")
    assert comp is True

    # Equivalent commercial grades
    comp2, msg2 = assess_grade_compatibility("Grade A", "FAQ")
    assert comp2 is True

    # Incompatible grades
    comp3, msg3 = assess_grade_compatibility("Grade A", "Grade C")
    assert comp3 is False
    assert "Incompatible" in msg3

    # Unknown grade provisional
    comp4, msg4 = assess_grade_compatibility("Grade A", "unknown")
    assert comp4 is True
    assert "Provisional" in msg4


def test_price_range_calculation():
    records = [
        {"normalized_modal_price_per_kg": 20.0, "observation_date": "2026-10-21", "validation_status": "valid"},
        {"normalized_modal_price_per_kg": 24.0, "observation_date": "2026-10-21", "validation_status": "valid"},
        {"normalized_modal_price_per_kg": 22.0, "observation_date": "2026-10-21", "validation_status": "valid"},
    ]
    summary = calculate_price_range(records)
    assert summary["usable_markets_count"] == 3
    assert summary["lowest_price_per_kg"] == 20.0
    assert summary["highest_price_per_kg"] == 24.0
    assert summary["price_range_str"] == "₹20.00 to ₹24.00 per kg"
    assert summary["all_same_date"] is True
