from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # LLM
    gemini_api_key: str = ""
    openai_api_key: str = ""

    # Geocoding (optional — improves Indian address resolution)
    google_maps_api_key: str = ""

    # App
    app_name: str = "GeoSafe AI"
    debug: bool = False
    cors_origins: list[str] = ["http://localhost:3000", "https://geosafe-ai.vercel.app"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
