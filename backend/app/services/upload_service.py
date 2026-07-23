"""Upload service — business logic for the Video Upload stage.

This is the **first stage** of the FlowMind pipeline:

    Upload -> Frame Extraction -> Audio Extraction -> OCR -> Transcription
           -> Workflow Graph -> Documentation -> RAG

Its single responsibility is: validate the incoming video, stream it to
`storage/uploads/`, compute its checksum, and record its metadata. No
processing happens here — later stages will read the file this service wrote
(located deterministically via `upload_id`) and drive `status` forward; this
service only ever writes `UploadStatus.UPLOADED`.
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
from app.schemas.upload import UploadCreateResponse, UploadRead
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
        """Validate, persist to disk, checksum, and record a new upload.

        Raises:
            UnsupportedFileTypeError: extension or declared content-type isn't MP4.
            FileTooLargeError: the stream exceeds `settings.max_upload_size_mb`
                (raised by `save_upload_stream`, propagated unchanged).
        """
        self._validate_file_type(filename=filename, content_type=content_type)

        upload_id = uuid.uuid4()
        extension = Path(filename).suffix.lower()
        destination = build_storage_path(self._settings.upload_dir, upload_id, extension)
        max_bytes = self._settings.max_upload_size_mb * 1024 * 1024

        saved_file = await save_upload_stream(destination, chunks, max_bytes=max_bytes)

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

        return UploadCreateResponse(upload_id=upload.id, status=upload.status)

    async def get_upload(self, upload_id: uuid.UUID) -> UploadRead | None:
        upload = await self._repository.get_by_id(upload_id)
        return UploadRead.model_validate(upload) if upload else None

    def _validate_file_type(self, *, filename: str, content_type: str) -> None:
        if not file_extension_allowed(filename, self._settings.allowed_upload_extensions):
            raise UnsupportedFileTypeError(
                "Only MP4 files are supported. Allowed extensions: "
                f"{', '.join(self._settings.allowed_upload_extensions)}"
            )
        if not mime_type_allowed(content_type, self._settings.allowed_upload_mime_types):
            raise UnsupportedFileTypeError(
                "Only MP4 files are supported. Allowed content types: "
                f"{', '.join(self._settings.allowed_upload_mime_types)}"
            )