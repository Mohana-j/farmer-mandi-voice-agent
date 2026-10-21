"""Configuration management for Farmer Mandi Price Voice Agent."""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ENVIRONMENT: str = "development"
    PROJECT_NAME: str = "Farmer Mandi Price Voice Agent"
    VERSION: str = "1.0.0"

    # Database
    DATABASE_URL: str = "sqlite:///./mandi_agent.db"

    # Data Provider: 'synthetic' (default demo mode) or 'live' (official public portal)
    DATA_PROVIDER_MODE: str = "synthetic"

    # Live Portal (e.g., Open Government Data Platform / Agmarknet Resource API)
    LIVE_PORTAL_API_URL: str = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
    LIVE_PORTAL_API_KEY: str = ""
    LIVE_PORTAL_TIMEOUT_SECONDS: int = 8

    # AI / Gemini API
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # Exports directory
    EXPORT_DIRECTORY: str = "./exports"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def get_export_path(self) -> Path:
        p = Path(self.EXPORT_DIRECTORY)
        p.mkdir(parents=True, exist_ok=True)
        return p


settings = Settings()
