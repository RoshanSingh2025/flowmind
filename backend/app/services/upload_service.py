"""Upload service — business logic for the Video Upload stage.

This is the **first stage** of the FlowMind pipeline:

    Upload -> Frame Extraction -> Audio Extraction -> OCR -> Transcription
           -> Workflow Graph -> Documentation -> RAG

Its single responsibility is: validate the incoming video, stream it to
`storage/uploads/`, compute its checksum, extract technical metadata,
generate a thumbnail, and record everything in the database.
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from pathlib import Path

from app.core.config import Settings
from app.core.exceptions import UnsupportedFileTypeError
from app.core.logging import get_logger
from app.models.upload import Upload, UploadStatus
from app.repositories.upload_repository import UploadRepository
from app.schemas.upload import (
    ResultsResponse,
    UploadCreateResponse,
    UploadListResponse,
    UploadRead,
)
from app.utils.export import ExportableResults
from app.utils.ffmpeg import (
    FFmpegError,
    FFprobeError,
    generate_thumbnail,
    probe_video,
    select_thumbnail_timestamp,
)
from app.utils.files import (
    build_storage_path,
    file_extension_allowed,
    mime_type_allowed,
    save_upload_stream,
)

logger = get_logger(__name__)


class UploadService:
    def __init__(self, repository: UploadRepository, settings: Settings) -> None:
        self._repository = repository
        self._settings = settings

    async def create_upload(
        self,
        *,
        filename: str,
        content_type: str,
        chunks: AsyncIterator[bytes],
    ) -> UploadCreateResponse:
        """Validate, save, extract metadata, generate thumbnail, and record upload."""

        self._validate_file_type(
            filename=filename,
            content_type=content_type,
        )

        upload_id = uuid.uuid4()

        extension = Path(filename).suffix.lower()

        destination = build_storage_path(
            self._settings.upload_dir,
            upload_id,
            extension,
        )

        max_bytes = self._settings.max_upload_size_mb * 1024 * 1024

        saved_file = await save_upload_stream(
            destination,
            chunks,
            max_bytes=max_bytes,
        )

        upload = Upload(
            id=upload_id,
            original_filename=filename,
            stored_filename=destination.name,
            mime_type=content_type,
            file_size=saved_file.size_bytes,
            checksum=saved_file.checksum,
            status=UploadStatus.UPLOADED,
        )

        upload = await self._repository.add(upload)

        logger.info(
            "upload_created",
            upload_id=str(upload.id),
            original_filename=filename,
            file_size=saved_file.size_bytes,
            checksum=saved_file.checksum,
        )

        # -------------------------------------------------------
        # Extract metadata + generate thumbnail
        # -------------------------------------------------------

        try:
            metadata = await probe_video(destination)

            thumbnail_path = (
                Path(self._settings.upload_dir)
                / "thumbnails"
                / f"{upload.id}.jpg"
            )

            timestamp = select_thumbnail_timestamp(
                metadata.duration or 0.0
            )

            await generate_thumbnail(
                destination,
                thumbnail_path,
                timestamp,
            )

            upload.duration = metadata.duration
            upload.width = metadata.width
            upload.height = metadata.height
            upload.fps = metadata.fps
            upload.codec = metadata.codec
            upload.bitrate = metadata.bitrate
            upload.container_format = metadata.container_format
            upload.thumbnail_path = str(thumbnail_path)

            await self._repository.add(upload)

            logger.info(
                "upload_metadata_extracted",
                upload_id=str(upload.id),
                duration=metadata.duration,
                width=metadata.width,
                height=metadata.height,
                codec=metadata.codec,
            )

        except (FFprobeError, FFmpegError) as exc:
            logger.exception(
                "upload_metadata_failed",
                upload_id=str(upload.id),
                error=str(exc),
            )

        return UploadCreateResponse(
            upload_id=upload.id,
            status=upload.status,
        )

    async def get_upload(
        self,
        upload_id: uuid.UUID,
    ) -> UploadRead | None:
        upload = await self._repository.get_by_id(upload_id)
        return UploadRead.model_validate(upload) if upload else None

    async def get_results(self, upload_id: uuid.UUID) -> ResultsResponse | None:
        upload = await self._repository.get_by_id(upload_id)
        if upload is None:
            return None
        return ResultsResponse(
            upload_id=upload.id,
            status=upload.status,
            original_filename=upload.original_filename,
            thumbnail_path=upload.thumbnail_path,
            transcript=upload.transcript,
            documentation=upload.documentation_markdown,
            sop=upload.sop_markdown,
            faq=upload.faq_markdown,
            summary=upload.summary_markdown,
            error=upload.processing_error,
        )

    async def list_uploads(
        self,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> UploadListResponse:
        uploads = await self._repository.list_all(limit=limit, offset=offset)
        total = await self._repository.count()
        return UploadListResponse(
            items=[UploadRead.model_validate(upload) for upload in uploads],
            total=total,
            limit=limit,
            offset=offset,
        )

    async def get_exportable_results(self, upload_id: uuid.UUID) -> ExportableResults | None:
        upload = await self._repository.get_by_id(upload_id)
        if upload is None:
            return None
        return ExportableResults(
            original_filename=upload.original_filename,
            summary=upload.summary_markdown,
            documentation=upload.documentation_markdown,
            sop=upload.sop_markdown,
            faq=upload.faq_markdown,
            transcript=upload.transcript,
        )

    async def get_thumbnail_path(self, upload_id: uuid.UUID) -> Path | None:
        """Returns the thumbnail file path for `upload_id` if one was
        generated AND the file still exists on disk. Returns `None` if the
        upload doesn't exist, metadata extraction failed (so no thumbnail
        was ever generated), or the file has since been removed."""
        upload = await self._repository.get_by_id(upload_id)
        if upload is None or not upload.thumbnail_path:
            return None
        path = Path(upload.thumbnail_path)
        return path if path.exists() else None

    def _validate_file_type(
        self,
        *,
        filename: str,
        content_type: str,
    ) -> None:
        if not file_extension_allowed(
            filename,
            self._settings.allowed_upload_extensions,
        ):
            raise UnsupportedFileTypeError(
                "Only MP4 files are supported. Allowed extensions: "
                f"{', '.join(self._settings.allowed_upload_extensions)}"
            )

        if not mime_type_allowed(
            content_type,
            self._settings.allowed_upload_mime_types,
        ):
            raise UnsupportedFileTypeError(
                "Only MP4 files are supported. Allowed content types: "
                f"{', '.join(self._settings.allowed_upload_mime_types)}"
            )