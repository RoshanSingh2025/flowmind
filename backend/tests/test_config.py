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
    # Explicitly pass the default values rather than relying on `Settings`'
    # field defaults: real environment variables (e.g. CI's `SECRET_KEY`)
    # take precedence over field defaults regardless of `_env_file`, so
    # asserting the guard is skipped for non-production requires pinning
    # the inputs directly rather than depending on ambient env state.
    settings = Settings(
        _env_file=None,
        environment=Environment.DEVELOPMENT,
        secret_key="dev-only-insecure-secret-key",
        database_url="sqlite+aiosqlite:///./flowmind.db",
    )
    assert settings.secret_key == "dev-only-insecure-secret-key"


def test_test_environment_ignores_dev_defaults() -> None:
    # See note above: pin secret_key/database_url explicitly so this test
    # doesn't depend on whatever DATABASE_URL/SECRET_KEY the environment
    # (e.g. GitHub Actions) happens to export.
    settings = Settings(
        _env_file=None,
        environment=Environment.TEST,
        secret_key="dev-only-insecure-secret-key",
        database_url="sqlite+aiosqlite:///:memory:",
    )
    assert settings.database_url.startswith("sqlite")
