"""Upload repository — persistence access for the `uploads` table."""

from __future__ import annotations

from app.models.upload import Upload
from app.repositories.base import BaseRepository


class UploadRepository(BaseRepository[Upload]):
    model = Upload
