"""Upload request/response schemas.

These are the only representation of an upload that ever crosses the API
boundary — the `Upload` ORM model (`app.models.upload.Upload`) never leaks
into a response directly.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.upload import UploadStatus


class UploadCreateResponse(BaseModel):
    """Response returned by `POST /api/v1/uploads`.

    Intentionally minimal — this endpoint only accepts and stores the file.
    Callers that need the full metadata record (checksum, size, etc.) fetch it
    via `GET /api/v1/uploads/{upload_id}`.
    """

    upload_id: uuid.UUID
    status: UploadStatus = Field(examples=[UploadStatus.UPLOADED])


class UploadRead(BaseModel):
    """Full upload metadata record, returned by `GET /api/v1/uploads/{upload_id}`."""

    model_config = ConfigDict(from_attributes=True)

    upload_id: uuid.UUID = Field(validation_alias="id")
    original_filename: str
    stored_filename: str
    mime_type: str
    file_size: int
    checksum: str
    status: UploadStatus
    created_at: datetime

    # --- Technical metadata (populated by ffprobe during upload) ---
    # All optional: `None` until metadata extraction succeeds, and remains
    # `None` forever for uploads where it failed (see
    # `UploadService.create_upload`'s `except (FFprobeError, FFmpegError)`
    # handling, which logs and continues rather than failing the upload).
    duration: float | None = None
    width: int | None = None
    height: int | None = None
    fps: float | None = None
    codec: str | None = None
    bitrate: int | None = None
    container_format: str | None = None

    # Raw server-side filesystem path — NOT a loadable URL. There is
    # currently no static mount or route that serves this file over HTTP;
    # exposing the path here is harmless (useful for debugging/future wiring)
    # but a frontend client cannot use this directly as an <img src>.
    thumbnail_path: str | None = None