"""Explicit, validated application configuration."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration supplied through environment variables or a local .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="APP_",
        case_sensitive=False,
        extra="ignore",
    )

    application_name: str = "AI Video Annotation Platform"
    environment: Literal["development", "test", "staging", "production"]
    secret_key: SecretStr
    database_url: str
    redis_url: str
    cors_origins: list[str] = Field(min_length=1)
    access_token_ttl_seconds: int = Field(default=900, ge=60, le=3600)
    refresh_token_ttl_seconds: int = Field(default=2_592_000, ge=86_400, le=7_776_000)
    jwt_issuer: str = "ai-video-annotation-platform"
    jwt_audience: str = "ai-video-annotation-platform-api"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    """Return one immutable settings instance per process."""

    return Settings()
