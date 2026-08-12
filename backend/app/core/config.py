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

from pydantic import AnyHttpUrl, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Insecure placeholder values. Fine for local development (zero-setup), but
# `Settings` refuses to start in production if either is still in effect —
# see `_forbid_insecure_production_defaults` below.
_INSECURE_DEV_SECRET_KEY = "dev-only-insecure-secret-key"
_DEV_DATABASE_URL_PREFIX = "sqlite"


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
    secret_key: str = Field(default=_INSECURE_DEV_SECRET_KEY)

    # --- CORS ---
    backend_cors_origins: list[AnyHttpUrl] | list[str] = ["http://localhost:3000"]

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

    # --- Transcription (faster-whisper, local, free) ---
    whisper_model_size: str = "base"
    whisper_device: str = "cpu"
    whisper_compute_type: str = "int8"

    # --- Document generation (Gemini API, free tier) ---
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-3.5-flash"
    gemini_timeout: int = 60

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def _split_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str) and not value.startswith("["):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @model_validator(mode="after")
    def _forbid_insecure_production_defaults(self) -> Settings:
        """Refuse to start in production with dev-only configuration.

        Checked here (rather than only at request time) so a misconfigured
        production deployment fails immediately at process startup — the
        first place `Settings()` is constructed — instead of serving traffic
        with an insecure secret key or against the local SQLite dev/test
        database. Development/staging/test are unaffected.
        """
        if self.environment != Environment.PRODUCTION:
            return self

        problems: list[str] = []
        if self.secret_key == _INSECURE_DEV_SECRET_KEY:
            problems.append("SECRET_KEY is still set to the insecure development default")
        if self.database_url.startswith(_DEV_DATABASE_URL_PREFIX):
            problems.append("DATABASE_URL points at the local SQLite development/test database")

        if problems:
            # Deliberately omit the actual secret_key/database_url values —
            # only names the problem, never the insecure value itself.
            raise ValueError(
                "Refusing to start with ENVIRONMENT=production: " + "; ".join(problems)
            )

        return self

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
