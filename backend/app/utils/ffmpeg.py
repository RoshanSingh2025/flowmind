"""Async utility module for interacting with FFmpeg and FFprobe.

Provides video metadata extraction (via ffprobe) and thumbnail generation
(via ffmpeg). This module is intentionally self-contained: it must never
import FastAPI, SQLAlchemy, the Upload model, the repository layer, or the
service layer. Callers are responsible for wiring its output into the rest
of the application.
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

from app.core.config import get_settings

settings = get_settings()

__all__ = [
    "VideoMetadata",
    "FFprobeError",
    "FFmpegError",
    "probe_video",
    "generate_thumbnail",
    "select_thumbnail_timestamp",
    "extract_audio",
]

_THUMBNAIL_TARGET_WIDTH = 640


class FFprobeError(Exception):
    """Raised when ffprobe fails to run, times out, or returns unusable output."""


class FFmpegError(Exception):
    """Raised when ffmpeg fails to run, times out, or fails to produce a thumbnail."""


@dataclass(frozen=True, slots=True)
class VideoMetadata:
    """Technical metadata extracted from a video file via ffprobe.

    Any field ffprobe couldn't determine is `None` rather than omitted, so
    callers can always rely on every attribute being present.
    """

    duration: float | None
    width: int | None
    height: int | None
    fps: float | None
    codec: str | None
    bitrate: int | None
    container_format: str | None


async def probe_video(video_path: Path) -> VideoMetadata:
    """Extract technical metadata from a video file using ffprobe.

    Args:
        video_path: Path to the video file to inspect.

    Returns:
        A `VideoMetadata` instance describing the video's duration, frame
        dimensions, frame rate, codec, bitrate, and container format.

    Raises:
        FFprobeError: `video_path` does not exist, `ffprobe` is not
            installed/found at `settings.ffprobe_path`, the process times
            out, exits with a non-zero return code, its output cannot be
            parsed as valid JSON, or no video stream is present.
    """
    _ensure_file_exists(video_path)

    command = [
        settings.ffprobe_path,
        "-v",
        "error",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        str(video_path),
    ]

    stdout = await _run_subprocess(
        command,
        error_type=FFprobeError,
        binary_name="ffprobe",
        timeout_message=f"ffprobe timed out while probing {video_path}",
    )

    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise FFprobeError(
            f"Could not parse ffprobe output as JSON for {video_path}: {exc}"
        ) from exc

    return _parse_probe_payload(payload, video_path)


def select_thumbnail_timestamp(duration: float) -> float:
    """Choose the timestamp (in seconds) at which to capture a thumbnail.

    Args:
        duration: Duration of the video in seconds.

    Returns:
        `5.0` if `duration` is greater than 10 seconds; otherwise
        `duration / 2` (the video's midpoint).
    """
    if duration > 10:
        return 5.0
    return duration / 2


async def generate_thumbnail(video_path: Path, output_path: Path, timestamp: float) -> None:
    """Capture a single frame from a video as a thumbnail image using ffmpeg.

    Seeks to `timestamp` seconds into `video_path`, captures exactly one
    frame, scales it to approximately `640` pixels wide while preserving
    aspect ratio, and writes it to `output_path`. `output_path`'s parent
    directory is created if it doesn't already exist, and any existing file
    at `output_path` is overwritten.

    Args:
        video_path: Path to the source video file.
        output_path: Path the captured frame should be written to (e.g. a
            `.jpg` file).
        timestamp: Position in seconds to seek to before capturing the frame.

    Raises:
        FFmpegError: `video_path` does not exist, `ffmpeg` is not
            installed/found at `settings.ffmpeg_path`, the process times
            out, exits with a non-zero return code, or does not produce a
            file at `output_path`.
    """
    _ensure_file_exists(video_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    command = [
        settings.ffmpeg_path,
        "-y",
        "-ss",
        f"{timestamp:.3f}",
        "-i",
        str(video_path),
        "-frames:v",
        "1",
        "-vf",
        f"scale={_THUMBNAIL_TARGET_WIDTH}:-2",
        "-q:v",
        "2",
        str(output_path),
    ]

    await _run_subprocess(
        command,
        error_type=FFmpegError,
        binary_name="ffmpeg",
        timeout_message=f"ffmpeg timed out while generating a thumbnail for {video_path}",
    )

    if not output_path.exists():
        raise FFmpegError(
            f"ffmpeg reported success but no thumbnail was produced at {output_path}"
        )


async def extract_audio(video_path: Path, output_path: Path) -> None:
    """Extract the audio track from a video as 16kHz mono WAV (faster-whisper's
    expected input format), using ffmpeg.

    `output_path`'s parent directory is created if it doesn't already exist,
    and any existing file at `output_path` is overwritten.

    Args:
        video_path: Path to the source video file.
        output_path: Path the extracted audio should be written to (e.g. a
            `.wav` file).

    Raises:
        FFmpegError: `video_path` does not exist, `ffmpeg` is not
            installed/found at `settings.ffmpeg_path`, the process times
            out, exits with a non-zero return code (e.g. the video has no
            audio track), or does not produce a file at `output_path`.
    """
    _ensure_file_exists(video_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    command = [
        settings.ffmpeg_path,
        "-y",
        "-i",
        str(video_path),
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-acodec",
        "pcm_s16le",
        str(output_path),
    ]

    await _run_subprocess(
        command,
        error_type=FFmpegError,
        binary_name="ffmpeg",
        timeout_message=f"ffmpeg timed out while extracting audio from {video_path}",
    )

    if not output_path.exists():
        raise FFmpegError(
            f"ffmpeg reported success but no audio file was produced at {output_path}"
        )


def _ensure_file_exists(path: Path) -> None:
    """Raise a `FFprobeError`/`FFmpegError`-agnostic check that `path` exists.

    Args:
        path: Path expected to exist on disk.

    Raises:
        FileNotFoundError: `path` does not exist. Callers catch this and wrap
            it into the appropriate domain-specific error.
    """
    if not path.exists():
        raise FileNotFoundError(f"Video file not found: {path}")


async def _run_subprocess(
    command: list[str],
    *,
    error_type: type[Exception],
    binary_name: str,
    timeout_message: str,
) -> bytes:
    """Run `command` and return its stdout on success.

    Uses `subprocess.run` in a worker thread (via `asyncio.to_thread`) rather
    than `asyncio.create_subprocess_exec`. The latter requires the active
    event loop to support subprocesses — on Windows, `SelectorEventLoop`
    does not (raises `NotImplementedError`), and which loop is active can
    end up outside this app's control (e.g. uvicorn's `--reload` supervisor
    resets the loop policy after app import, regardless of `--loop` flags
    or policy set at startup). Plain `subprocess.run` has no such
    dependency, so this works identically under any event loop, on any OS.

    Args:
        command: The full command (binary + arguments) to execute.
        error_type: Exception class to raise on any failure (`FFprobeError`
            or `FFmpegError`, depending on the caller).
        binary_name: Human-readable binary name, used in error messages.
        timeout_message: Message to raise if the process times out.

    Returns:
        The captured stdout bytes of the completed process.

    Raises:
        FileNotFoundError: propagated from `_ensure_file_exists`, called by
            callers before this function.
        error_type: the configured binary can't be found/executed, the
            process times out, or it exits with a non-zero return code.
    """
    import subprocess

    def _run() -> subprocess.CompletedProcess[bytes]:
        return subprocess.run(  # noqa: S603 - command list is built internally, not from user input
            command,
            capture_output=True,
            timeout=settings.ffmpeg_timeout,
        )

    try:
        result = await asyncio.to_thread(_run)
    except FileNotFoundError as exc:
        raise error_type(f"{binary_name} binary not found: {command[0]!r}") from exc
    except subprocess.TimeoutExpired as exc:
        raise error_type(timeout_message) from exc

    if result.returncode != 0:
        stderr_text = result.stderr.decode(errors="ignore").strip()
        raise error_type(
            f"{binary_name} exited with code {result.returncode}: {stderr_text}"
        )

    return result.stdout


def _parse_probe_payload(payload: dict, video_path: Path) -> VideoMetadata:
    """Parse ffprobe's raw JSON payload into a `VideoMetadata` instance.

    Args:
        payload: The decoded JSON object returned by `ffprobe -show_format
            -show_streams`.
        video_path: Original video path, used only for error messages.

    Returns:
        A populated `VideoMetadata` instance.

    Raises:
        FFprobeError: no video stream is present in `payload["streams"]`.
    """
    fmt: dict = payload.get("format") or {}
    streams: list[dict] = payload.get("streams") or []
    video_stream = next((s for s in streams if s.get("codec_type") == "video"), None)

    if video_stream is None:
        raise FFprobeError(f"No video stream found in {video_path}")

    duration = _to_float(fmt.get("duration"))
    if duration is None:
        duration = _to_float(video_stream.get("duration"))

    bitrate = _to_int(fmt.get("bit_rate"))
    if bitrate is None:
        bitrate = _to_int(video_stream.get("bit_rate"))

    raw_format_name = fmt.get("format_name") or ""
    container_format = raw_format_name.split(",")[0] or None

    width = _to_int(video_stream.get("width"))
    height = _to_int(video_stream.get("height"))
    codec = video_stream.get("codec_name")
    fps = _parse_frame_rate(video_stream.get("r_frame_rate")) or _parse_frame_rate(
        video_stream.get("avg_frame_rate")
    )

    return VideoMetadata(
        duration=duration,
        width=width,
        height=height,
        fps=fps,
        codec=codec,
        bitrate=bitrate,
        container_format=container_format,
    )


def _parse_frame_rate(value: str | None) -> float | None:
    """Parse ffprobe's `"30000/1001"`-style frame-rate fraction into a float fps.

    Args:
        value: The raw `r_frame_rate`/`avg_frame_rate` string from ffprobe,
            e.g. `"25/1"`, or `None`.

    Returns:
        The frame rate as a float rounded to 3 decimal places, or `None` if
        `value` is missing, malformed, or has a zero denominator.
    """
    if not value:
        return None
    try:
        fraction = Fraction(value)
    except (ValueError, ZeroDivisionError):
        return None
    if fraction.denominator == 0:
        return None
    return round(float(fraction), 3)


def _to_float(value: object) -> float | None:
    """Best-effort conversion of an ffprobe field to `float`, or `None`."""
    try:
        return float(value) if value is not None else None  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def _to_int(value: object) -> int | None:
    """Best-effort conversion of an ffprobe field to `int`, or `None`."""
    try:
        return int(float(value)) if value is not None else None  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
