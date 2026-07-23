"""Version endpoint — exposes the running build's name/version/API prefix."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import SettingsDep
from app.schemas.common import VersionResponse

router = APIRouter(tags=["system"])


@router.get("/version", response_model=VersionResponse, summary="Build/version info")
async def get_version(settings: SettingsDep) -> VersionResponse:
    return VersionResponse(
        name=settings.project_name,
        version=settings.version,
        api_prefix=settings.api_v1_prefix,
    )
