"""Regression tests for `PipelineService` persistence.

Exercises `PipelineService.process()` directly against the in-memory test
database (bypassing HTTP/ffmpeg/faster-whisper/Gemini), asserting that each
pipeline stage's output is actually committed to the `uploads` row — not
just held in memory — and specifically that a transcript already produced
by a successful transcription step is NOT lost if the later document
generation step fails.
"""

from __future__ import annotations

import hashlib
import uuid
from pathlib import Path

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.upload import Upload, UploadStatus
from app.repositories.upload_repository import UploadRepository
from app.services.document_generation_service import DocumentGenerationError, GeneratedDocuments
from app.services.pipeline_service import PipelineService

pytestmark = pytest.mark.asyncio


async def _create_uploaded_row(session: AsyncSession) -> Upload:
    upload = Upload(
        original_filename="demo.mp4",
        stored_filename=f"{uuid.uuid4()}.mp4",
        mime_type="video/mp4",
        file_size=1024,
        checksum=hashlib.sha256(b"fake").hexdigest(),
        status=UploadStatus.UPLOADED,
    )
    return await UploadRepository(session).add(upload)


class _FakeTranscriptionService:
    def __init__(self, transcript: str) -> None:
        self._transcript = transcript

    async def transcribe(self, audio_path: Path) -> str:
        return self._transcript


class _FakeDocumentServiceSuccess:
    async def generate(self, transcript: str) -> GeneratedDocuments:
        return GeneratedDocuments(
            documentation="# Docs", sop="# SOP", faq="# FAQ", summary="# Summary"
        )


class _FakeDocumentServiceFailure:
    async def generate(self, transcript: str) -> GeneratedDocuments:
        raise DocumentGenerationError("Gemini API returned 500: internal error")


async def _noop_extract_audio(video_path: Path, output_path: Path) -> None:
    return None


async def test_pipeline_persists_transcript_and_documents_on_success(
    db_session: AsyncSession, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("app.services.pipeline_service.extract_audio", _noop_extract_audio)

    upload = await _create_uploaded_row(db_session)
    await db_session.commit()

    service = PipelineService(
        session=db_session,
        settings=get_settings(),
        transcription_service=_FakeTranscriptionService("hello world"),
        document_service=_FakeDocumentServiceSuccess(),
    )
    await service.process(upload.id)

    persisted = await UploadRepository(db_session).get_by_id(upload.id)
    assert persisted is not None
    assert persisted.status == UploadStatus.COMPLETED
    assert persisted.transcript == "hello world"
    assert persisted.documentation_markdown == "# Docs"
    assert persisted.sop_markdown == "# SOP"
    assert persisted.faq_markdown == "# FAQ"
    assert persisted.summary_markdown == "# Summary"
    assert persisted.processing_error is None


async def test_pipeline_persists_transcript_even_when_document_generation_fails(
    db_session: AsyncSession, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Regression test: previously, a successful transcription followed by
    a failed document-generation step discarded the transcript entirely,
    because both were only ever written to the DB in a single commit at the
    very end of `process()`. The transcript must now survive on its own."""
    monkeypatch.setattr("app.services.pipeline_service.extract_audio", _noop_extract_audio)

    upload = await _create_uploaded_row(db_session)
    await db_session.commit()

    service = PipelineService(
        session=db_session,
        settings=get_settings(),
        transcription_service=_FakeTranscriptionService("this should survive"),
        document_service=_FakeDocumentServiceFailure(),
    )
    await service.process(upload.id)

    persisted = await UploadRepository(db_session).get_by_id(upload.id)
    assert persisted is not None
    assert persisted.status == UploadStatus.FAILED
    assert persisted.transcript == "this should survive"
    assert persisted.processing_error
    # Never leak the raw upstream error text to a persisted/API-visible field.
    assert "Gemini" not in persisted.processing_error
