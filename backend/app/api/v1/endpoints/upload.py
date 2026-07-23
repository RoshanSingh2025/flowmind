"""Upload endpoint — Video Upload Service.

First stage of the FlowMind pipeline. Accepts an MP4 video, persists it to
`storage/uploads/`, and records its metadata. Deliberately does **not**
trigger Frame Extraction, Audio Extraction, OCR, Transcription, Workflow
Graph, Documentation, or RAG — those are separate, not-yet-implemented
stages. The router only validates the HTTP contract and delegates everything
else to `UploadService`.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, UploadFile, status

from app.api.deps import UploadServiceDep
from app.core.exceptions import NotFoundError
from app.schemas.upload import UploadCreateResponse, UploadRead
from app.utils.files import iter_upload_file

router = APIRouter(tags=["uploads"])


@router.post(
    "/uploads",
    response_model=UploadCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload an MP4 video (max 500MB). Storage only — no processing.",
)
async def create_upload(file: UploadFile, service: UploadServiceDep) -> UploadCreateResponse:
    return await service.create_upload(
        filename=file.filename or "unnamed",
        content_type=file.content_type or "application/octet-stream",
        chunks=iter_upload_file(file),
    )


@router.get(
    "/uploads/{upload_id}",
    response_model=UploadRead,
    summary="Fetch upload metadata by id",
)
async def get_upload(upload_id: uuid.UUID, service: UploadServiceDep) -> UploadRead:
    upload = await service.get_upload(upload_id)
    if upload is None:
        raise NotFoundError(f"Upload {upload_id} was not found")
    return upload