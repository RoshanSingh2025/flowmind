"""Application configuration.

Settings are loaded from environment variables / a `.env` file via
`pydantic-settings`. A single `Settings` class defines every configurable value;
environment-specific behaviour (e.g. docs enabled, CORS strictness, echo SQL) is
derived from the `environment` field rather than duplicated across classes, so
there is exactly one source of truth per key.

Usage:
    from app.core.config import get_settings
    settings = get_settings()
"""

from __future__ import annotations

from enum import StrEnum
from functools import lru_cache

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- App ---
    environment: Environment = Environment.DEVELOPMENT
    project_name: str = "FlowMind"
    version: str = "0.1.0"
    api_v1_prefix: str = "/api/v1"
    secret_key: str = Field(default="dev-only-insecure-secret-key")

    # --- CORS ---
    backend_cors_origins: list[AnyHttpUrl] | list[str] = [
        "http://localhost:3000"
    ]

    # --- Database ---
    database_url: str = "sqlite+aiosqlite:///./flowmind.db"
    database_echo: bool = False

    # --- Redis ---
    redis_url: str = "redis://localhost:6379/0"

    # --- Qdrant ---
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None

    # --- Logging ---
    log_level: str = "INFO"
    log_json: bool = True

    # --- Uploads ---
    upload_dir: str = "./storage/uploads"
    max_upload_size_mb: int = 500
    allowed_upload_extensions: list[str] = [".mp4"]
    allowed_upload_mime_types: list[str] = ["video/mp4"]

    # --- FFmpeg ---
    ffmpeg_path: str = "ffmpeg"
    ffprobe_path: str = "ffprobe"
    ffmpeg_timeout: int = 30

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def _split_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str) and not value.startswith("["):
            return [
                origin.strip()
                for origin in value.split(",")
                if origin.strip()
            ]
        return value

    @property
    def is_production(self) -> bool:
        return self.environment == Environment.PRODUCTION

    @property
    def is_development(self) -> bool:
        return self.environment == Environment.DEVELOPMENT

    @property
    def is_test(self) -> bool:
        return self.environment == Environment.TEST

    @property
    def docs_url(self) -> str | None:
        return None if self.is_production else "/docs"

    @property
    def redoc_url(self) -> str | None:
        return None if self.is_production else "/redoc"

    @property
    def openapi_url(self) -> str | None:
        return None if self.is_production else "/openapi.json"


@lru_cache
def get_settings() -> Settings:
    return Settings()