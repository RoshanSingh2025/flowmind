from __future__ import annotations

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_get_version_returns_project_metadata(client: AsyncClient) -> None:
    response = await client.get("/api/v1/version")

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "FlowMind"
    assert "version" in body
    assert body["api_prefix"] == "/api/v1"
