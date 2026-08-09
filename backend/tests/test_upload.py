from __future__ import annotations

import asyncio
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


def _real_mp4_bytes() -> bytes:
    """A tiny (~1s) but genuinely valid MP4 with video+audio, generated via
    ffmpeg. Needed wherever a test depends on real ffprobe/thumbnail
    generation succeeding — `_mp4_bytes()`'s fake content can't produce
    those (ffprobe correctly rejects it as not a video, so thumbnail
    generation is silently skipped, same as any other malformed upload)."""
    import subprocess
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "lavfi",
                "-i",
                "sine=frequency=440:duration=1",
                "-f",
                "lavfi",
                "-i",
                "color=c=blue:s=64x64:d=1",
                "-c:v",
                "libx264",
                "-c:a",
                "aac",
                "-shortest",
                tmp.name,
            ],
            capture_output=True,
            check=True,
        )
        return Path(tmp.name).read_bytes()


async def test_create_upload_returns_initial_uploaded_status(
    client: AsyncClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The POST response itself always reflects the immediate post-save
    state ("uploaded") — background processing happens after this response
    is already sent, so it can never affect what this endpoint returns."""
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
    # Status is no longer pinned to "uploaded" now that the background
    # pipeline actually runs (see test_pipeline.py for pipeline-specific
    # assertions) — this test is about metadata persistence, not outcome.
    assert body["status"] in {"uploaded", "processing", "completed", "failed"}
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


async def test_list_uploads_returns_newest_first(
    client: AsyncClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    ids = []
    for name in ("first.mp4", "second.mp4"):
        files = {"file": (name, io.BytesIO(_mp4_bytes()), "video/mp4")}
        response = await client.post("/api/v1/uploads", files=files)
        ids.append(response.json()["upload_id"])
        # SQLite's server-side now() has whole-second resolution; without
        # this, both uploads could land in the same second and "newest
        # first" would be untestable (see UploadRepository.list_all).
        await asyncio.sleep(1.05)

    response = await client.get("/api/v1/uploads")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 2
    assert body["limit"] == 20
    assert body["offset"] == 0
    returned_ids = [item["upload_id"] for item in body["items"]]
    # newest (second) upload must come before the older (first) one
    assert returned_ids.index(ids[1]) < returned_ids.index(ids[0])


async def test_list_uploads_respects_limit(client: AsyncClient) -> None:
    response = await client.get("/api/v1/uploads?limit=1&offset=0")

    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) <= 1
    assert body["limit"] == 1


async def test_get_thumbnail_returns_image_for_valid_video(
    client: AsyncClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    files = {"file": ("real.mp4", io.BytesIO(_real_mp4_bytes()), "video/mp4")}

    create_response = await client.post("/api/v1/uploads", files=files)
    upload_id = create_response.json()["upload_id"]

    response = await client.get(f"/api/v1/uploads/{upload_id}/thumbnail")

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpeg"
    assert len(response.content) > 0


async def test_get_thumbnail_returns_404_when_extraction_failed(
    client: AsyncClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Fake (non-video) bytes mean ffprobe/thumbnail generation silently
    fail during upload (see UploadService.create_upload) — no thumbnail_path
    is ever set, so this must 404, not error."""
    monkeypatch.chdir(tmp_path)
    files = {"file": ("fake.mp4", io.BytesIO(_mp4_bytes()), "video/mp4")}

    create_response = await client.post("/api/v1/uploads", files=files)
    upload_id = create_response.json()["upload_id"]

    response = await client.get(f"/api/v1/uploads/{upload_id}/thumbnail")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


async def test_get_thumbnail_returns_404_for_unknown_upload(client: AsyncClient) -> None:
    response = await client.get(f"/api/v1/uploads/{uuid.uuid4()}/thumbnail")

    assert response.status_code == 404


async def test_retry_upload_resets_failed_upload_to_uploaded(
    client: AsyncClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, db_session
) -> None:
    from app.models.upload import UploadStatus
    from app.repositories.upload_repository import UploadRepository

    monkeypatch.chdir(tmp_path)
    files = {"file": ("demo.mp4", io.BytesIO(_mp4_bytes()), "video/mp4")}
    create_response = await client.post("/api/v1/uploads", files=files)
    upload_id = create_response.json()["upload_id"]

    # Force it into a failed state directly, as if the pipeline had already run.
    repository = UploadRepository(db_session)
    upload = await repository.get_by_id(uuid.UUID(upload_id))
    assert upload is not None
    upload.status = UploadStatus.FAILED
    upload.processing_error = "something went wrong"
    await repository.add(upload)
    await db_session.commit()

    response = await client.post(f"/api/v1/uploads/{upload_id}/retry")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "uploaded"
    assert body["processing_error"] is None


async def test_retry_upload_rejects_non_failed_status(
    client: AsyncClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, db_session
) -> None:
    from app.models.upload import UploadStatus
    from app.repositories.upload_repository import UploadRepository

    monkeypatch.chdir(tmp_path)
    files = {"file": ("demo.mp4", io.BytesIO(_mp4_bytes()), "video/mp4")}
    create_response = await client.post("/api/v1/uploads", files=files)
    upload_id = create_response.json()["upload_id"]

    # Fake bytes mean the background pipeline already ran and set this to
    # "failed" by the time the POST above returns — force it to
    # "completed" instead, so this test actually exercises the
    # non-failed-status rejection path rather than accidentally hitting an
    # already-failed upload (which retry would legitimately accept).
    repository = UploadRepository(db_session)
    upload = await repository.get_by_id(uuid.UUID(upload_id))
    assert upload is not None
    upload.status = UploadStatus.COMPLETED
    await repository.add(upload)
    await db_session.commit()

    response = await client.post(f"/api/v1/uploads/{upload_id}/retry")

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "conflict"


async def test_retry_upload_returns_404_for_unknown_upload(client: AsyncClient) -> None:
    response = await client.post(f"/api/v1/uploads/{uuid.uuid4()}/retry")

    assert response.status_code == 404
