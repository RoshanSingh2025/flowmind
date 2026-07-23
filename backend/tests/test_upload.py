from __future__ import annotations

import hashlib
import io
import uuid
from pathlib import Path

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from app.core.config import Settings, get_settings

pytestmark = pytest.mark.asyncio


def _mp4_bytes(payload: bytes = b"fake mp4 video bytes") -> bytes:
    return payload


async def test_create_upload_persists_metadata_and_does_not_process(
    client: AsyncClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    content = _mp4_bytes()
    files = {"file": ("demo.mp4", io.BytesIO(content), "video/mp4")}

    response = await client.post("/api/v1/uploads", files=files)

    assert response.status_code == 201
    body = response.json()
    assert set(body.keys()) == {"upload_id", "status"}
    assert body["status"] == "uploaded"
    uuid.UUID(body["upload_id"])  # raises if not a valid UUID


async def test_uploaded_file_is_saved_under_storage_uploads(
    client: AsyncClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    content = _mp4_bytes()
    files = {"file": ("demo.mp4", io.BytesIO(content), "video/mp4")}

    response = await client.post("/api/v1/uploads", files=files)
    upload_id = response.json()["upload_id"]

    expected_path = tmp_path / "storage" / "uploads" / f"{upload_id}.mp4"
    assert expected_path.exists()
    assert expected_path.read_bytes() == content


async def test_get_upload_returns_full_metadata_with_checksum(
    client: AsyncClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    content = _mp4_bytes()
    files = {"file": ("demo.mp4", io.BytesIO(content), "video/mp4")}

    create_response = await client.post("/api/v1/uploads", files=files)
    upload_id = create_response.json()["upload_id"]

    get_response = await client.get(f"/api/v1/uploads/{upload_id}")

    assert get_response.status_code == 200
    body = get_response.json()
    assert body["upload_id"] == upload_id
    assert body["original_filename"] == "demo.mp4"
    assert body["stored_filename"] == f"{upload_id}.mp4"
    assert body["mime_type"] == "video/mp4"
    assert body["file_size"] == len(content)
    assert body["checksum"] == hashlib.sha256(content).hexdigest()
    assert body["status"] == "uploaded"
    assert "created_at" in body


async def test_create_upload_rejects_non_mp4_extension(
    client: AsyncClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    files = {"file": ("demo.mov", io.BytesIO(b"noop"), "video/quicktime")}

    response = await client.post("/api/v1/uploads", files=files)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "unsupported_file_type"


async def test_create_upload_rejects_mismatched_mime_type(
    client: AsyncClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A `.mp4` extension with a non-MP4 declared content-type must be rejected too."""
    monkeypatch.chdir(tmp_path)
    files = {"file": ("demo.mp4", io.BytesIO(b"noop"), "video/quicktime")}

    response = await client.post("/api/v1/uploads", files=files)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "unsupported_file_type"


async def test_create_upload_rejects_file_exceeding_max_size(
    test_app: FastAPI, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Enforces the size cap without needing to actually allocate 500MB in a test."""
    monkeypatch.chdir(tmp_path)

    def _tiny_limit_settings() -> Settings:
        return Settings(max_upload_size_mb=0, allowed_upload_extensions=[".mp4"])

    # `max_upload_size_mb=0` bytes -> any non-empty file exceeds the limit,
    # letting the test exercise the real streaming/abort path with a small payload.
    test_app.dependency_overrides[get_settings] = _tiny_limit_settings

    from httpx import ASGITransport, AsyncClient

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        files = {"file": ("demo.mp4", io.BytesIO(b"x" * 1024), "video/mp4")}
        response = await client.post("/api/v1/uploads", files=files)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "file_too_large"

    # the partially-written file must not be left behind on disk
    uploads_dir = tmp_path / "storage" / "uploads"
    leftover_files = list(uploads_dir.glob("*")) if uploads_dir.exists() else []
    assert leftover_files == []


async def test_get_upload_returns_404_for_unknown_id(client: AsyncClient) -> None:
    response = await client.get(f"/api/v1/uploads/{uuid.uuid4()}")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"