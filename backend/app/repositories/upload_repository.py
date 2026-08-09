"""Upload repository — persistence access for the `uploads` table."""

from __future__ import annotations

from sqlalchemy import select

from app.models.upload import Upload
from app.repositories.base import BaseRepository


class UploadRepository(BaseRepository[Upload]):
    model = Upload

    async def list_all(self, *, limit: int = 100, offset: int = 0) -> list[Upload]:
        """Newest-first — matches Dashboard expectations. Ties on `created_at`
        (e.g. two uploads within the same second — SQLite's `now()` only has
        second-level resolution) are broken by `id` for a deterministic,
        stable order across pages. Postgres in production has microsecond
        resolution, so ties there are rarer, but the tiebreaker is harmless
        and keeps pagination stable either way."""
        result = await self.session.execute(
            select(Upload)
            .order_by(Upload.created_at.desc(), Upload.id.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
