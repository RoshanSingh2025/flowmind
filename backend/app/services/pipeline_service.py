"""Background processing pipeline.

Orchestrates the second stage of FlowMind (the first being upload/storage,
in `UploadService`):

    uploaded -> processing -> (extract audio -> transcribe -> generate docs) -> completed
                                                                              -> failed

Runs via FastAPI `BackgroundTasks` (no external queue/broker — see the
project's tech constraints). This means the task shares the request
process: it survives as long as the server process does, but does not
survive a server restart or retry automatically. Acceptable for the current
scale; revisit if durability/retries become a requirement.
"""

from __future__ import annotations

import uuid
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import Settings
from app.core.logging import get_logger
from app.models.upload import UploadStatus
from app.repositories.upload_repository import UploadRepository
from app.services.document_generation_service import (
    DocumentGenerationError,
    GeminiDocumentGenerationService,
)
from app.services.transcription_service import (
    FasterWhisperTranscriptionService,
    TranscriptionError,
)
from app.utils.ffmpeg import FFmpegError, extract_audio

logger = get_logger(__name__)


class PipelineService:
    def __init__(
        self,
        *,
        session: AsyncSession,
        settings: Settings,
        transcription_service: FasterWhisperTranscriptionService | None = None,
        document_service: GeminiDocumentGenerationService | None = None,
    ) -> None:
        self._session = session
        self._settings = settings
        self._repository = UploadRepository(session)
        self._transcription_service = transcription_service or FasterWhisperTranscriptionService(
            settings
        )
        self._document_service = document_service or GeminiDocumentGenerationService(settings)

    async def process(self, upload_id: uuid.UUID) -> None:
        """Runs the full pipeline for one upload. Never raises — all
        failures are caught, logged, and recorded on the upload record as
        `status=FAILED` + `processing_error`, since this runs detached from
        any request that could otherwise surface an exception."""
        upload = await self._repository.get_by_id(upload_id)
        if upload is None:
            logger.error("pipeline_upload_not_found", upload_id=str(upload_id))
            return

        upload.status = UploadStatus.PROCESSING
        await self._repository.add(upload)
        await self._session.commit()
        logger.info("pipeline_started", upload_id=str(upload_id))

        audio_path = (
            Path(self._settings.upload_dir) / "audio" / f"{upload_id}.wav"
        )

        try:
            video_path = Path(self._settings.upload_dir) / upload.stored_filename

            await extract_audio(video_path, audio_path)
            logger.info("pipeline_audio_extracted", upload_id=str(upload_id))

            transcript = await self._transcription_service.transcribe(audio_path)
            logger.info(
                "pipeline_transcribed", upload_id=str(upload_id), transcript_length=len(transcript)
            )

            # Persist the transcript as soon as it exists, in its own
            # commit — rather than waiting until after document generation
            # too. Previously a Gemini failure right after a successful
            # transcription meant the transcript was never written (the
            # exception handler below runs before the later
            # `upload.transcript = transcript` assignment ever executes),
            # silently discarding real work.
            upload.transcript = transcript
            await self._repository.add(upload)
            await self._session.commit()
            logger.info("pipeline_transcript_persisted", upload_id=str(upload_id))

            documents = await self._document_service.generate(transcript)
            logger.info("pipeline_documents_generated", upload_id=str(upload_id))

            upload.documentation_markdown = documents.documentation
            upload.sop_markdown = documents.sop
            upload.faq_markdown = documents.faq
            upload.summary_markdown = documents.summary
            upload.status = UploadStatus.COMPLETED
            upload.processing_error = None

        except (FFmpegError, TranscriptionError, DocumentGenerationError) as exc:
            # Full detail (may include filesystem paths / upstream response
            # bodies) goes to logs only. The public `/results` endpoint
            # surfaces `processing_error` to any caller, so it must stay
            # generic — never leak internal paths, stack traces, or
            # upstream (e.g. Gemini) error bodies to API consumers.
            logger.exception("pipeline_failed", upload_id=str(upload_id), error=str(exc))
            upload.status = UploadStatus.FAILED
            upload.processing_error = (
                "Processing failed while preparing this video. Please try again; "
                "if the problem persists, contact support."
            )

        except Exception as exc:  # noqa: BLE001 - last-resort guard, this runs detached
            logger.exception(
                "pipeline_failed_unexpected", upload_id=str(upload_id), error=str(exc)
            )
            upload.status = UploadStatus.FAILED
            upload.processing_error = (
                "An unexpected error occurred while processing this video. "
                "Please try again; if the problem persists, contact support."
            )

        finally:
            audio_path.unlink(missing_ok=True)

        await self._repository.add(upload)
        await self._session.commit()
        logger.info("pipeline_finished", upload_id=str(upload_id), status=upload.status)


async def run_pipeline_in_background(
    upload_id: uuid.UUID,
    settings: Settings,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """Entry point for `BackgroundTasks.add_task`.

    Takes `session_factory` as a parameter (rather than importing
    `AsyncSessionLocal` directly) for two reasons: it opens its own session
    independent of the request's lifecycle (this task can run for minutes —
    ffmpeg + whisper + Gemini — and holding a request-scoped session open
    that long is fragile), and it keeps this testable: tests override the
    `get_session_factory` dependency to point at the same in-memory test
    database used for the request path.
    """
    async with session_factory() as session:
        service = PipelineService(session=session, settings=settings)
        await service.process(upload_id)