"""Market data adapter connecting to official public agricultural portals or synthetic fixtures."""

from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional, Tuple
import httpx
from bs4 import BeautifulSoup

from backend.app.config import settings
from backend.app.services.demo_data import get_synthetic_market_fixtures

logger = logging.getLogger(__name__)


class MarketDataAdapter:
    """Retrieves mandi price records with full provenance tracking.
    
    Supports:
    1. 'synthetic' mode: deterministic test fixtures tagged explicitly as data_mode='synthetic'.
    2. 'live' mode: connects to official Open Government Data / Agmarknet public API endpoint.
       If live portal is offline, rate-limited, or unauthorized, falls back transparently with
       explicit notice so the user is never misled.
    """

    def __init__(self, mode: Optional[str] = None):
        self.mode = mode or settings.DATA_PROVIDER_MODE

    async def fetch_market_records(
        self,
        crop: str = "tomato",
        location: str = "Dharmapuri",
        radius_km: float = 50.0,
        force_yesterday_only: bool = False,
    ) -> Tuple[List[Dict[str, Any]], str, Dict[str, Any]]:
        """Fetch records with provenance.
        
        Returns:
            (records_list, active_mode, metadata)
        """
        now = datetime.now(timezone.utc)
        metadata: Dict[str, Any] = {
            "requested_mode": self.mode,
            "retrieval_timestamp": now.isoformat(),
            "target_crop": crop,
            "target_location": location,
        }

        if self.mode == "live":
            try:
                records, live_meta = await self._fetch_live_portal(crop, location)
                if records:
                    metadata.update(live_meta)
                    return records, "live", metadata
                else:
                    logger.warning("Live portal returned 0 records. Falling back to synthetic mode.")
                    metadata["fallback_reason"] = "Live portal returned 0 records for current search"
            except Exception as exc:
                logger.warning(f"Live portal connection failed ({exc}). Falling back to synthetic mode.")
                metadata["fallback_reason"] = f"Live portal connection error: {str(exc)}"

        # Default or fallback: synthetic fixtures
        records = get_synthetic_market_fixtures(
            crop=crop,
            location=location,
            radius_km=radius_km,
            force_yesterday_only=force_yesterday_only,
        )
        metadata["effective_mode"] = "synthetic"
        metadata["fixture_source"] = "Agmarknet Historical / Simulation Fixtures"
        return records, "synthetic", metadata

    async def _fetch_live_portal(
        self,
        crop: str,
        location: str,
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Attempt to fetch from official public mandi portal (Open Government Data API / Agmarknet)."""
        api_url = settings.LIVE_PORTAL_API_URL
        api_key = settings.LIVE_PORTAL_API_KEY
        timeout = settings.LIVE_PORTAL_TIMEOUT_SECONDS

        if not api_key:
            raise ValueError("LIVE_PORTAL_API_KEY is not configured. Live government portal access requires valid key.")

        params = {
            "api-key": api_key,
            "format": "json",
            "filters[commodity]": crop.capitalize(),
            "limit": 10,
        }

        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(api_url, params=params)
            resp.raise_for_response()
            data = resp.json()

        records_raw = data.get("records", [])
        parsed_records: List[Dict[str, Any]] = []
        now = datetime.now(timezone.utc)

        for idx, item in enumerate(records_raw):
            market_name = item.get("market") or f"{location} Mandi"
            min_p = float(item["min_price"]) if item.get("min_price") else None
            max_p = float(item["max_price"]) if item.get("max_price") else None
            modal_p = float(item["modal_price"]) if item.get("modal_price") else None
            obs_date = item.get("arrival_date") or now.strftime("%Y-%m-%d")

            parsed_records.append({
                "source_id": "gov-data-portal",
                "source_url": api_url,
                "source_record_id": f"GOV-{item.get('state', 'IND')}-{idx+1:03d}",
                "market_name": market_name,
                "market_location": f"{item.get('district', location)}, {item.get('state', '')}".strip(", "),
                "distance_km": None,  # Live portal doesn't provide GPS distance
                "crop": item.get("commodity", crop).capitalize(),
                "grade": item.get("grade", "FAQ"),
                "original_price_min": min_p,
                "original_price_max": max_p,
                "original_modal_price": modal_p,
                "original_unit": "INR/quintal",  # Standard Agmarknet unit
                "observation_date": obs_date,
                "retrieved_at": now.isoformat(),
                "data_mode": "live",
            })

        return parsed_records, {
            "live_portal_records_found": len(parsed_records),
            "source_endpoint": api_url,
        }
