import os
from functools import lru_cache

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    database_url: str = Field(
        default="sqlite:///./pricing.db",
        description="SQLAlchemy database URL. Defaults to local SQLite for development.",
    )
    allowed_cors_origins: list[str] = Field(default_factory=lambda: ["*"])

    class Config:
        env_file = ".env"
        env_prefix = "PRICING_"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
