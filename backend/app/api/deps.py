"""Dependency-injection wiring.

Routers depend on functions here, never directly on repositories/sessions.
This keeps `api/` a thin HTTP layer and makes every service trivially
swappable in tests via FastAPI's `app.dependency_overrides`.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import Settings, get_settings
from app.database.session import get_db_session, get_session_factory
from app.repositories.upload_repository import UploadRepository
from app.services.upload_service import UploadService

SettingsDep = Annotated[Settings, Depends(get_settings)]
DBSessionDep = Annotated[AsyncSession, Depends(get_db_session)]
SessionFactoryDep = Annotated[async_sessionmaker[AsyncSession], Depends(get_session_factory)]


def get_upload_repository(session: DBSessionDep) -> UploadRepository:
    return UploadRepository(session)


UploadRepositoryDep = Annotated[UploadRepository, Depends(get_upload_repository)]


def get_upload_service(
    repository: UploadRepositoryDep,
    settings: SettingsDep,
) -> UploadService:
    return UploadService(repository=repository, settings=settings)


UploadServiceDep = Annotated[UploadService, Depends(get_upload_service)]
