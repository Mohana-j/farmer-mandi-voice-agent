"""Deterministic synthetic data provider for demo and offline test cases."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional


def get_synthetic_market_fixtures(
    crop: str = "tomato",
    location: str = "Dharmapuri",
    radius_km: float = 50.0,
    force_yesterday_only: bool = False,
    include_mixed_units: bool = True,
) -> List[Dict[str, Any]]:
    """Generate deterministic synthetic market records with authentic agricultural parameters.
    
    All synthetic records are clearly labelled data_mode='synthetic'.
    """
    now = datetime.now(timezone.utc)
    today_str = now.strftime("%Y-%m-%d")
    yesterday_str = (now - timedelta(days=1)).strftime("%Y-%m-%d")

    crop_normalized = crop.strip().lower()

    if crop_normalized == "tomato":
        if force_yesterday_only:
            # All records are yesterday's date
            return [
                {
                    "source_id": "synthetic-fixture-tn",
                    "source_url": "https://agmarknet.gov.in/SearchCmmMkt.aspx?demo=fixture-tc2",
                    "source_record_id": "SYN-TC2-001",
                    "market_name": "Dharmapuri Regulated Market",
                    "market_location": "Dharmapuri, Tamil Nadu",
                    "distance_km": 12.5,
                    "crop": "Tomato",
                    "grade": "Grade A",
                    "original_price_min": 2100.0,
                    "original_price_max": 2400.0,
                    "original_modal_price": 2250.0,
                    "original_unit": "INR/quintal",
                    "observation_date": yesterday_str,
                    "retrieved_at": now.isoformat(),
                    "data_mode": "synthetic",
                },
                {
                    "source_id": "synthetic-fixture-tn",
                    "source_url": "https://agmarknet.gov.in/SearchCmmMkt.aspx?demo=fixture-tc2",
                    "source_record_id": "SYN-TC2-002",
                    "market_name": "Palacode APMC",
                    "market_location": "Palacode, Dharmapuri",
                    "distance_km": 24.0,
                    "crop": "Tomato",
                    "grade": "Grade A",
                    "original_price_min": 2200.0,
                    "original_price_max": 2500.0,
                    "original_modal_price": 2350.0,
                    "original_unit": "INR/quintal",
                    "observation_date": yesterday_str,
                    "retrieved_at": now.isoformat(),
                    "data_mode": "synthetic",
                },
            ]

        # Standard tomato records
        records = [
            {
                "source_id": "synthetic-fixture-tn",
                "source_url": "https://agmarknet.gov.in/SearchCmmMkt.aspx?demo=fixture-dhp",
                "source_record_id": "SYN-DHP-001",
                "market_name": "Palacode APMC",
                "market_location": "Palacode, Dharmapuri",
                "distance_km": 18.2,
                "crop": "Tomato",
                "grade": "Grade A",
                "original_price_min": 2000.0,
                "original_price_max": 2400.0,
                "original_modal_price": 2200.0,
                "original_unit": "INR/quintal",  # 22 INR/kg
                "observation_date": today_str,
                "retrieved_at": now.isoformat(),
                "data_mode": "synthetic",
            },
            {
                "source_id": "synthetic-fixture-tn",
                "source_url": "https://agmarknet.gov.in/SearchCmmMkt.aspx?demo=fixture-dhp",
                "source_record_id": "SYN-DHP-002",
                "market_name": "Dharmapuri Regulated Market",
                "market_location": "Dharmapuri Town",
                "distance_km": 8.5,
                "crop": "Tomato",
                "grade": "Grade A",
                "original_price_min": 18.0,
                "original_price_max": 23.0,
                "original_modal_price": 21.0,
                "original_unit": "INR/kg" if include_mixed_units else "INR/quintal",
                "observation_date": today_str,
                "retrieved_at": now.isoformat(),
                "data_mode": "synthetic",
            },
            {
                "source_id": "synthetic-fixture-tn",
                "source_url": "https://agmarknet.gov.in/SearchCmmMkt.aspx?demo=fixture-dhp",
                "source_record_id": "SYN-DHP-003",
                "market_name": "Pennagaram Uzhavar Sandhai",
                "market_location": "Pennagaram, Dharmapuri",
                "distance_km": 31.0,
                "crop": "Tomato",
                "grade": "Grade A",
                "original_price_min": 2300.0,
                "original_price_max": 2600.0,
                "original_modal_price": 2400.0,
                "original_unit": "INR/quintal",  # 24 INR/kg
                "observation_date": today_str,
                "retrieved_at": now.isoformat(),
                "data_mode": "synthetic",
            },
            {
                "source_id": "synthetic-fixture-tn",
                "source_url": "https://agmarknet.gov.in/SearchCmmMkt.aspx?demo=fixture-dhp",
                "source_record_id": "SYN-DHP-004",
                "market_name": "Krishnagiri Market",
                "market_location": "Krishnagiri District",
                "distance_km": 54.0,  # Outside default 50km
                "crop": "Tomato",
                "grade": "Grade A",
                "original_price_min": 2500.0,
                "original_price_max": 2800.0,
                "original_modal_price": 2650.0,
                "original_unit": "INR/quintal",
                "observation_date": today_str,
                "retrieved_at": now.isoformat(),
                "data_mode": "synthetic",
            },
        ]
        return records

    elif crop_normalized in ("onion", "வெங்காயம்"):
        return [
            {
                "source_id": "synthetic-fixture-tn",
                "source_url": "https://agmarknet.gov.in/SearchCmmMkt.aspx?demo=fixture-onion",
                "source_record_id": "SYN-ON-001",
                "market_name": "Dharmapuri Regulated Market",
                "market_location": "Dharmapuri Town",
                "distance_km": 8.5,
                "crop": "Onion",
                "grade": "Grade A",
                "original_price_min": 3200.0,
                "original_price_max": 3800.0,
                "original_modal_price": 3500.0,
                "original_unit": "INR/quintal",
                "observation_date": today_str,
                "retrieved_at": now.isoformat(),
                "data_mode": "synthetic",
            },
            {
                "source_id": "synthetic-fixture-tn",
                "source_url": "https://agmarknet.gov.in/SearchCmmMkt.aspx?demo=fixture-onion",
                "source_record_id": "SYN-ON-002",
                "market_name": "Palacode APMC",
                "market_location": "Palacode, Dharmapuri",
                "distance_km": 18.2,
                "crop": "Onion",
                "grade": "Grade A",
                "original_price_min": 3300.0,
                "original_price_max": 3900.0,
                "original_modal_price": 3600.0,
                "original_unit": "INR/quintal",
                "observation_date": today_str,
                "retrieved_at": now.isoformat(),
                "data_mode": "synthetic",
            },
        ]

    else:
        # Generic crop fixture
        return [
            {
                "source_id": "synthetic-fixture-gen",
                "source_url": "https://agmarknet.gov.in/SearchCmmMkt.aspx?demo=fixture-gen",
                "source_record_id": "SYN-GEN-001",
                "market_name": f"{location} Primary Market",
                "market_location": location,
                "distance_km": 10.0,
                "crop": crop.capitalize(),
                "grade": "Grade A",
                "original_price_min": 1800.0,
                "original_price_max": 2200.0,
                "original_modal_price": 2000.0,
                "original_unit": "INR/quintal",
                "observation_date": today_str,
                "retrieved_at": now.isoformat(),
                "data_mode": "synthetic",
            },
            {
                "source_id": "synthetic-fixture-gen",
                "source_url": "https://agmarknet.gov.in/SearchCmmMkt.aspx?demo=fixture-gen",
                "source_record_id": "SYN-GEN-002",
                "market_name": f"{location} Regional Mandi",
                "market_location": location,
                "distance_km": 25.0,
                "crop": crop.capitalize(),
                "grade": "Grade A",
                "original_price_min": 21.0,
                "original_price_max": 25.0,
                "original_modal_price": 23.0,
                "original_unit": "INR/kg",
                "observation_date": today_str,
                "retrieved_at": now.isoformat(),
                "data_mode": "synthetic",
            },
        ]
