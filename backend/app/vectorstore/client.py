"""Qdrant client wrapper (reserved for the AI knowledge-base phase).

Intentionally minimal today: it only proves connectivity is wired end-to-end
(config → client → infra). Collection management, upsert, and similarity
search methods will be added once the embedding pipeline is approved.
"""

from __future__ import annotations

from functools import lru_cache

from qdrant_client import AsyncQdrantClient

from app.core.config import get_settings


@lru_cache
def get_qdrant_client() -> AsyncQdrantClient:
    settings = get_settings()
    return AsyncQdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)
