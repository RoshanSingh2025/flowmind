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