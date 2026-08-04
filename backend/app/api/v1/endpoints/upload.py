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

from fastapi import APIRouter, BackgroundTasks, Query, UploadFile, status
from fastapi.responses import Response

from app.api.deps import SessionFactoryDep, SettingsDep, UploadServiceDep
from app.core.exceptions import NotFoundError
from app.schemas.upload import (
    ResultsResponse,
    UploadCreateResponse,
    UploadListResponse,
    UploadRead,
)
from app.services.pipeline_service import run_pipeline_in_background
from app.utils.export import build_markdown_bundle, build_pdf_bundle
from app.utils.files import iter_upload_file

router = APIRouter(tags=["uploads"])


@router.post(
    "/uploads",
    response_model=UploadCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload an MP4 video (max 500MB) and queue it for processing.",
)
async def create_upload(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    service: UploadServiceDep,
    settings: SettingsDep,
    session_factory: SessionFactoryDep,
) -> UploadCreateResponse:
    result = await service.create_upload(
        filename=file.filename or "unnamed",
        content_type=file.content_type or "application/octet-stream",
        chunks=iter_upload_file(file),
    )
    background_tasks.add_task(
        run_pipeline_in_background, result.upload_id, settings, session_factory
    )
    return result


@router.get(
    "/uploads",
    response_model=UploadListResponse,
    summary="List uploads, newest first (paginated)",
)
async def list_uploads(
    service: UploadServiceDep,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> UploadListResponse:
    return await service.list_uploads(limit=limit, offset=offset)


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


@router.get(
    "/uploads/{upload_id}/results",
    response_model=ResultsResponse,
    summary="Fetch generated documentation/SOP/FAQ/summary for an upload",
)
async def get_results(upload_id: uuid.UUID, service: UploadServiceDep) -> ResultsResponse:
    results = await service.get_results(upload_id)
    if results is None:
        raise NotFoundError(f"Upload {upload_id} was not found")
    return results


@router.get(
    "/uploads/{upload_id}/export/markdown",
    summary="Export generated documents as a single Markdown file",
)
async def export_markdown(upload_id: uuid.UUID, service: UploadServiceDep) -> Response:
    results = await service.get_exportable_results(upload_id)
    if results is None:
        raise NotFoundError(f"Upload {upload_id} was not found")
    body = build_markdown_bundle(results)
    return Response(
        content=body,
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{upload_id}.md"'},
    )


@router.get(
    "/uploads/{upload_id}/export/pdf",
    summary="Export generated documents as a PDF",
)
async def export_pdf(upload_id: uuid.UUID, service: UploadServiceDep) -> Response:
    results = await service.get_exportable_results(upload_id)
    if results is None:
        raise NotFoundError(f"Upload {upload_id} was not found")
    body = build_pdf_bundle(results)
    return Response(
        content=body,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{upload_id}.pdf"'},
    )