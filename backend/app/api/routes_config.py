"""Health and configuration API endpoints."""

from fastapi import APIRouter
from backend.app.config import settings

router = APIRouter(tags=["System"])


@router.get("/health")
def get_health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "data_provider_mode": settings.DATA_PROVIDER_MODE,
        "gemini_api_configured": bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your_gemini_api_key_here"),
    }


@router.get("/config")
def get_config():
    """Client configuration endpoint with safe public settings."""
    return {
        "project_name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "data_provider_mode": settings.DATA_PROVIDER_MODE,
        "gemini_api_configured": bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your_gemini_api_key_here"),
        "live_portal_api_configured": bool(settings.LIVE_PORTAL_API_KEY),
        "default_language": "en",
        "supported_languages": ["en", "ta"],
    }
