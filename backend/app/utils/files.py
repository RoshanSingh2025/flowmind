"""Filesystem helpers for storing uploaded files.

Kept deliberately simple (local disk) for the foundation phase. Swapping this
for S3/GCS later only requires changing this module — services depend on the
functions below, not on `pathlib`/disk layout directly.
"""

from __future__ import annotations

import hashlib
import os
import uuid
from collections.abc import AsyncIterable
from dataclasses import dataclass
from pathlib import Path

import aiofiles

from app.core.exceptions import FileTooLargeError


def build_storage_path(upload_dir: str, upload_id: uuid.UUID, extension: str) -> Path:
    """Return the on-disk path for a given upload id.

    The stored filename is derived from `upload_id` (not a fresh random name)
    so the ORM row and the file on disk always share the same identity —
    later pipeline stages (frame extraction, OCR, ...) can locate a file from
    the upload id alone without a lookup.
    """
    return Path(upload_dir) / f"{upload_id}{extension.lower()}"


async def iter_upload_file(file, chunk_size: int = 1024 * 1024):  # noqa: ANN001
    """Yield an `UploadFile`'s content in fixed-size chunks without loading it all into memory."""
    while chunk := await file.read(chunk_size):
        yield chunk


@dataclass(frozen=True)
class SavedFile:
    """Result of streaming an upload to disk."""

    size_bytes: int
    checksum: str  # hex-encoded SHA-256 digest


async def save_upload_stream(
    destination: Path,
    chunks: AsyncIterable[bytes],
    *,
    max_bytes: int | None = None,
) -> SavedFile:
    """Stream-write an upload to disk while computing its SHA-256 checksum.

    Size and checksum are computed in the same pass so the file is only read
    once. If `max_bytes` is exceeded mid-stream, writing stops immediately and
    the partial file is removed rather than being left orphaned on disk.
    """
    destination.parent.mkdir(parents=True, exist_ok=True)

    total_bytes = 0
    digest = hashlib.sha256()

    try:
        async with aiofiles.open(destination, "wb") as buffer:
            async for chunk in chunks:
                total_bytes += len(chunk)
                if max_bytes is not None and total_bytes > max_bytes:
                    raise FileTooLargeError(
                        f"File exceeds maximum allowed size of {max_bytes} bytes"
                    )
                digest.update(chunk)
                await buffer.write(chunk)
    except FileTooLargeError:
        destination.unlink(missing_ok=True)  # noqa: ASYNC240 - trivial cleanup, not on hot path
        raise

    return SavedFile(size_bytes=total_bytes, checksum=digest.hexdigest())


def file_extension_allowed(filename: str, allowed_extensions: list[str]) -> bool:
    return Path(filename).suffix.lower() in {ext.lower() for ext in allowed_extensions}


def mime_type_allowed(content_type: str, allowed_mime_types: list[str]) -> bool:
    return content_type.lower() in {mime.lower() for mime in allowed_mime_types}


def human_readable_size(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}TB"


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)