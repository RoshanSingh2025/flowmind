"""Unit tests for the production startup config guard (`app.core.config`).

Uses `_env_file=None` so these are hermetic and independent of whatever the
local `backend/.env` happens to contain.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.core.config import Environment, Settings

_SAFE_SECRET_KEY = "a-sufficiently-random-production-secret"
_SAFE_DATABASE_URL = "postgresql+asyncpg://flowmind:flowmind@db:5432/flowmind"


def test_production_rejects_default_secret_key() -> None:
    with pytest.raises(ValidationError, match="SECRET_KEY"):
        Settings(
            _env_file=None,
            environment=Environment.PRODUCTION,
            secret_key="dev-only-insecure-secret-key",
            database_url=_SAFE_DATABASE_URL,
        )


def test_production_rejects_sqlite_database_url() -> None:
    with pytest.raises(ValidationError, match="DATABASE_URL"):
        Settings(
            _env_file=None,
            environment=Environment.PRODUCTION,
            secret_key=_SAFE_SECRET_KEY,
            database_url="sqlite+aiosqlite:///./flowmind.db",
        )


def test_production_error_does_not_leak_secret_value() -> None:
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            _env_file=None,
            environment=Environment.PRODUCTION,
            secret_key="dev-only-insecure-secret-key",
            database_url=_SAFE_DATABASE_URL,
        )
    assert "dev-only-insecure-secret-key" not in str(exc_info.value)


def test_production_accepts_safe_configuration() -> None:
    settings = Settings(
        _env_file=None,
        environment=Environment.PRODUCTION,
        secret_key=_SAFE_SECRET_KEY,
        database_url=_SAFE_DATABASE_URL,
    )
    assert settings.is_production


def test_development_ignores_dev_defaults() -> None:
    settings = Settings(_env_file=None, environment=Environment.DEVELOPMENT)
    assert settings.secret_key == "dev-only-insecure-secret-key"


def test_test_environment_ignores_dev_defaults() -> None:
    settings = Settings(_env_file=None, environment=Environment.TEST)
    assert settings.database_url.startswith("sqlite")
