from __future__ import annotations

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_health_check_returns_ok(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "environment" in body


async def test_health_check_includes_request_id_header(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health")

    assert "x-request-id" in response.headers
