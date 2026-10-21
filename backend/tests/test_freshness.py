"""Tests for data freshness classification and date evaluation."""

from datetime import date, timedelta
import pytest
from backend.app.services.normalizer import evaluate_data_freshness


def test_today_freshness():
    ref_date = date(2026, 10, 21)
    status, msg = evaluate_data_freshness("2026-10-21", reference_date=ref_date)
    assert status == "today"
    assert "Current data" in msg


def test_yesterday_freshness():
    ref_date = date(2026, 10, 21)
    yesterday_str = (ref_date - timedelta(days=1)).strftime("%Y-%m-%d")
    status, msg = evaluate_data_freshness(yesterday_str, reference_date=ref_date)
    assert status == "yesterday"
    assert "Yesterday's data" in msg


def test_older_freshness():
    ref_date = date(2026, 10, 21)
    older_str = (ref_date - timedelta(days=5)).strftime("%Y-%m-%d")
    status, msg = evaluate_data_freshness(older_str, reference_date=ref_date)
    assert status == "older"
    assert "5 days old" in msg


def test_missing_and_invalid_date():
    status, _ = evaluate_data_freshness("")
    assert status == "unknown"

    status2, _ = evaluate_data_freshness("not-a-date")
    assert status2 == "unknown"
