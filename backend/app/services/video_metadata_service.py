from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.utils.ffmpeg import (
    FFmpegError,
    FFprobeError,
    VideoMetadata,
    generate_thumbnail as _generate_thumbnail_file,
    probe_video as _probe_video_file,
    select_thumbnail_timestamp,
)

__all__ = [
    "VideoMetadataService",
    "VideoProcessingResult",
    "FFmpegError",
    "FFprobeError",
]


@dataclass(frozen=True, slots=True)
class VideoProcessingResult:
    metadata: VideoMetadata
    thumbnail_path: Path


class VideoMetadataService:
    async def probe(self, video_path: Path) -> VideoMetadata:
        return await _probe_video_file(video_path)

    async def generate_thumbnail(
        self,
        video_path: Path,
        thumbnail_path: Path,
        timestamp: float | None = None,
    ) -> Path:
        resolved_timestamp = timestamp
        if resolved_timestamp is None:
            metadata = await self.probe(video_path)
            resolved_timestamp = select_thumbnail_timestamp(metadata.duration or 0.0)
        await _generate_thumbnail_file(video_path, thumbnail_path, resolved_timestamp)
        return thumbnail_path

    async def process(self, video_path: Path, thumbnail_path: Path) -> VideoProcessingResult:
        metadata = await self.probe(video_path)
        timestamp = select_thumbnail_timestamp(metadata.duration or 0.0)
        await _generate_thumbnail_file(video_path, thumbnail_path, timestamp)
        return VideoProcessingResult(metadata=metadata, thumbnail_path=thumbnail_path)