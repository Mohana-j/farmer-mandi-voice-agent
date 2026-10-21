"""Deterministic unit conversion, grade compatibility, and price range calculation."""

from datetime import date, datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple, Any


SUPPORTED_UNITS = {
    "inr/kg": 1.0,
    "rs/kg": 1.0,
    "inr per kg": 1.0,
    "kg": 1.0,
    "inr/quintal": 100.0,
    "rs/quintal": 100.0,
    "quintal": 100.0,
    "inr per quintal": 100.0,
    "inr/tonne": 1000.0,
    "rs/tonne": 1000.0,
    "tonne": 1000.0,
    "metric tonne": 1000.0,
    "inr per tonne": 1000.0,
}


def normalize_unit_to_kg(price: Optional[float], unit: str) -> Tuple[Optional[float], Optional[str]]:
    """Convert price to INR/kg using deterministic conversion factors.
    
    Returns:
        (normalized_price_per_kg, error_or_warning_message)
    """
    if price is None:
        return None, "Price value is absent or null"

    if not unit or not isinstance(unit, str):
        return None, "Unit specification is missing"

    unit_clean = unit.strip().lower()
    conversion_factor = SUPPORTED_UNITS.get(unit_clean)

    if conversion_factor is None:
        return None, f"Unsupported unit '{unit}'. Cannot assume conversion factor."

    # Calculation: INR/unit / (kg in unit) = INR/kg
    normalized = round(price / conversion_factor, 2)
    return normalized, None


def assess_grade_compatibility(query_grade: str, record_grade: str) -> Tuple[bool, str]:
    """Check whether record grade is compatible with the farmer's query grade.
    
    Rules:
    - Never compare incompatible grades as if they were identical.
    - If either grade is unknown or unverified, comparisons are marked provisional.
    - If grades match or both are standard commercial grades (e.g. 'Grade A', 'FAQ', 'Standard'), compatible.
    """
    q = (query_grade or "").strip().lower()
    r = (record_grade or "").strip().lower()

    if not q or q == "unknown" or not r or r == "unknown":
        return True, "Provisional comparison: one or both grades are unverified"

    if q == r:
        return True, "Compatible grades"

    # Commercial equivalence classes
    top_grades = {"grade a", "faq", "standard", "medium", "super"}
    second_grades = {"grade b", "fair", "small"}
    reject_grades = {"grade c", "damaged", "reject"}

    if q in top_grades and r in top_grades:
        return True, f"Compatible standard grades ({query_grade} vs {record_grade})"

    if q in second_grades and r in second_grades:
        return True, f"Compatible secondary grades ({query_grade} vs {record_grade})"

    return False, f"Incompatible grades: query asked for '{query_grade}', but market record is '{record_grade}'"


def evaluate_data_freshness(observation_date_str: str, reference_date: Optional[date] = None) -> Tuple[str, str]:
    """Evaluate whether observation date is today, yesterday, older, or unknown.
    
    Returns:
        (freshness_category, explanation)
    """
    if not observation_date_str:
        return "unknown", "Observation date is missing or not provided by source"

    if reference_date is None:
        # Use UTC or local reference date (current date)
        reference_date = datetime.now(timezone.utc).date()

    try:
        # Parse YYYY-MM-DD
        obs_date = datetime.strptime(observation_date_str.strip()[:10], "%Y-%m-%d").date()
    except Exception:
        try:
            # Try DD-MM-YYYY
            obs_date = datetime.strptime(observation_date_str.strip()[:10], "%d-%m-%Y").date()
        except Exception:
            return "unknown", f"Unparseable date format '{observation_date_str}'"

    delta_days = (reference_date - obs_date).days

    if delta_days == 0:
        return "today", "Current data (observed today)"
    elif delta_days == 1:
        return "yesterday", f"Yesterday's data (observed on {obs_date.isoformat()})"
    elif delta_days > 1:
        return "older", f"Older data ({delta_days} days old, observed on {obs_date.isoformat()})"
    else:
        # Observation date in the future?
        return "provisional", f"Future observation date recorded ({obs_date.isoformat()})"


def calculate_price_range(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate lower bound, upper bound, and summary from usable normalized records.
    
    Explicitly retains distinction between min, max, and modal prices.
    """
    usable_prices = []
    excluded_count = 0
    dates = set()
    sources = set()
    has_incompatible = False
    has_unverified = False

    for r in records:
        val_status = r.get("validation_status", "valid")
        if val_status == "valid" or val_status == "provisional":
            # Prefer modal price, fallback to min or max or average
            p = r.get("normalized_modal_price_per_kg")
            if p is None:
                p_min = r.get("normalized_price_min_per_kg")
                p_max = r.get("normalized_price_max_per_kg")
                if p_min is not None and p_max is not None:
                    p = round((p_min + p_max) / 2.0, 2)
                elif p_min is not None:
                    p = p_min
                elif p_max is not None:
                    p = p_max

            if p is not None:
                usable_prices.append(p)
                if r.get("observation_date"):
                    dates.add(r.get("observation_date"))
                if r.get("source_id"):
                    sources.add(r.get("source_id"))
            else:
                excluded_count += 1
        else:
            excluded_count += 1
            if val_status == "incompatible_grade":
                has_incompatible = True

        if val_status == "provisional":
            has_unverified = True

    if not usable_prices:
        return {
            "lowest_price_per_kg": None,
            "highest_price_per_kg": None,
            "price_range_str": "No usable market records available",
            "usable_markets_count": 0,
            "excluded_markets_count": excluded_count,
            "all_same_date": True,
            "dates_observed": list(dates),
            "freshness_summary": "No data",
            "grade_compatibility_note": "Incompatible grades found" if has_incompatible else "No records evaluated",
            "profitability_disclaimer": "Transport cost is unknown. The most profitable market cannot be determined from price alone.",
            "source_names": list(sources),
        }

    lowest = min(usable_prices)
    highest = max(usable_prices)

    if lowest == highest:
        range_str = f"₹{lowest:.2f} per kg"
    else:
        range_str = f"₹{lowest:.2f} to ₹{highest:.2f} per kg"

    all_same = (len(dates) <= 1)

    grade_note = "All included records have compatible grades."
    if has_unverified:
        grade_note = "Comparison includes unverified grades and is provisional."

    return {
        "lowest_price_per_kg": lowest,
        "highest_price_per_kg": highest,
        "price_range_str": range_str,
        "usable_markets_count": len(usable_prices),
        "excluded_markets_count": excluded_count,
        "all_same_date": all_same,
        "dates_observed": sorted(list(dates)),
        "freshness_summary": f"Observed dates: {', '.join(sorted(dates))}",
        "grade_compatibility_note": grade_note,
        "profitability_disclaimer": "Transport cost is unknown. The most profitable market cannot be determined from price alone.",
        "source_names": list(sources),
    }
