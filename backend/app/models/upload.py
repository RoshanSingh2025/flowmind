"""Upload ORM model.

Represents a video uploaded to FlowMind. This is the **first stage** of a
larger asynchronous pipeline:

    Upload -> Frame Extraction -> Audio Extraction -> OCR -> Transcription
           -> Workflow Graph -> Documentation -> RAG

Only upload metadata is persisted here — none of the later stages are
implemented yet. `status` exists specifically so those future stages have a
field to transition through (`uploaded` -> `queued` -> `processing` -> ...)
without requiring a schema change; `checksum` exists so later stages (and a
future dedup/idempotency check) can identify identical uploads without
re-reading the file from disk.
"""

from __future__ import annotations

import enum

from sqlalchemy import BigInteger, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class UploadStatus(str, enum.Enum):
    """Lifecycle of an uploaded video through the FlowMind pipeline.

    Only `UPLOADED` is ever set by this service. The remaining members are
    reserved for future pipeline stages (frame/audio extraction, OCR,
    transcription, workflow graph, documentation, RAG) and are not
    transitioned to anywhere in this codebase yet.
    """

    UPLOADED = "uploaded"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Upload(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "uploads"

    # `id` (from UUIDPrimaryKeyMixin) is the upload's identity — referred to as
    # `upload_id` at the API boundary (see app.schemas.upload).
    original_filename: Mapped[str] = mapped_column(String(512), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    mime_type: Mapped[str] = mapped_column(String(128), nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    checksum: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    status: Mapped[UploadStatus] = mapped_column(
        Enum(UploadStatus, name="upload_status", native_enum=False),
        default=UploadStatus.UPLOADED,
        nullable=False,
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return (
            f"<Upload id={self.id} original_filename={self.original_filename!r} "
            f"status={self.status}>"
        )