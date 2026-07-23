"""Datetime helpers used across services."""

from __future__ import annotations

from datetime import UTC, datetime


def utc_now() -> datetime:
    """Return a timezone-aware UTC `datetime`."""
    return datetime.now(UTC)
