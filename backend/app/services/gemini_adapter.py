"""Google Gemini API adapter with transparent deterministic fallback."""

import logging
from typing import Any, Dict, Optional
import httpx

from backend.app.config import settings

logger = logging.getLogger(__name__)


class GeminiAdapter:
    """Manages LLM reasoning and query parsing.
    
    If GEMINI_API_KEY is not set or API call fails, transparently falls back to
    deterministic rule-based parsing and logs the execution mode accurately.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL
        self.is_configured = bool(self.api_key and self.api_key.strip() and self.api_key != "your_gemini_api_key_here")

    async def parse_farmer_query(self, transcript: str) -> Dict[str, Any]:
        """Extract crop, grade, location, radius, and language from farmer query transcript.
        
        Returns parsed parameters and indicates whether LLM or deterministic fallback was used.
        """
        if self.is_configured:
            try:
                result = await self._call_gemini_parse(transcript)
                result["engine"] = "gemini-api"
                return result
            except Exception as e:
                logger.warning(f"Gemini API parse failed: {e}. Falling back to deterministic parser.")

        # Deterministic fallback parser
        result = self._deterministic_parse(transcript)
        result["engine"] = "deterministic-rule-engine"
        return result

    def _deterministic_parse(self, text: str) -> Dict[str, Any]:
        """High-accuracy rule-based natural language parser for farmer queries."""
        t = (text or "").lower()

        # Language detection (Tamil unicode range)
        has_tamil = any("\u0b80" <= char <= "\u0bff" for char in text)
        language = "ta" if has_tamil else "en"

        # Crop detection
        crop = "tomato"
        crop_keywords = {
            "tomato": ["tomato", "tomatoes", "தக்காளி", "thakkali"],
            "onion": ["onion", "onions", "வெங்காயம்", "vengayam"],
            "potato": ["potato", "potatoes", "உருளைக்கிழங்கு", "urulaikizhangu"],
            "chilli": ["chilli", "chili", "chillies", "மிளகாய்", "milagai"],
            "brinjal": ["brinjal", "eggplant", "கத்தரிக்காய்", "kathirikai"],
            "cabbage": ["cabbage", "முட்டைக்கோஸ்", "muttaikose"],
        }
        for c_name, keywords in crop_keywords.items():
            if any(k in t for k in keywords):
                crop = c_name
                break

        # Grade detection
        grade = "Grade A"
        if "grade b" in t or "second" in t or "இரண்டாம் தரம்" in t:
            grade = "Grade B"
        elif "grade c" in t or "third" in t:
            grade = "Grade C"
        elif "faq" in t or "standard" in t or "சராசரி தரம்" in t:
            grade = "FAQ"
        elif "unverified" in t or "unknown" in t:
            grade = "unknown"

        # Location detection
        location = "Dharmapuri"
        known_locations = [
            "dharmapuri", "palacode", "pennagaram", "krishnagiri", "salem",
            "kolar", "hosur", "dindigul", "madurai", "coimbatore", "vellore",
            "தர்மபுரி", "பாலக்கோடு", "கிருஷ்ணகிரி", "சேலம்"
        ]
        for loc in known_locations:
            if loc in t:
                location = loc.capitalize()
                break

        # Radius detection (looking for numbers before km or கிலோமீட்டர்)
        radius_km = 50.0
        import re
        radius_match = re.search(r"(\d+)\s*(?:km|kms|kilometer|kilometres|கிலோமீட்டர்)", t)
        if radius_match:
            try:
                val = float(radius_match.group(1))
                if 5.0 <= val <= 500.0:
                    radius_km = val
            except Exception:
                pass

        return {
            "crop": crop,
            "grade": grade,
            "location": location,
            "radius_km": radius_km,
            "language": language,
            "parsed_from_text": text,
        }

    async def _call_gemini_parse(self, text: str) -> Dict[str, Any]:
        """Invoke Google Gemini REST API using httpx."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        prompt = (
            f"You are a structured parser for farmer agricultural voice queries in English and Tamil. "
            f"Analyze this input: \"{text}\"\n"
            f"Extract JSON with fields:\n"
            f"- crop (string, e.g. 'tomato', default 'tomato')\n"
            f"- grade (string, e.g. 'Grade A', 'Grade B', 'FAQ', or 'unknown')\n"
            f"- location (string, nearest town/market, default 'Dharmapuri')\n"
            f"- radius_km (number, search radius in km, default 50.0)\n"
            f"- language ('en' or 'ta')\n"
            f"Respond ONLY with valid JSON."
        )

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"}
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_response()
            data = resp.json()
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            import json
            return json.loads(raw_text)
