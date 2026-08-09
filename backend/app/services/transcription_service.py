"""Speech-to-text service.

Defines `TranscriptionService` as the interface the rest of the app depends
on, and `FasterWhisperTranscriptionService` as the current (local, free)
implementation. Swapping to a different provider (e.g. a hosted API) means
writing a new class that satisfies the same interface — nothing else in the
app changes.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from app.core.config import Settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class TranscriptionError(Exception):
    """Raised when speech-to-text fails for any reason."""


class TranscriptionService(Protocol):
    async def transcribe(self, audio_path: Path) -> str:
        """Return the full transcript text for the audio file at `audio_path`."""
        ...


class FasterWhisperTranscriptionService:
    """Local, offline speech-to-text using faster-whisper (CTranslate2-based
    Whisper). No API key, no per-request cost — the tradeoff is CPU time and
    a one-time model download on first use.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._model = None  # lazy-loaded: avoids paying model-load cost at import time

    def _get_model(self):
        if self._model is None:
            # Imported lazily so the (large) faster-whisper/ctranslate2
            # dependency is only touched by code paths that actually
            # transcribe, keeping app startup fast for everything else.
            from faster_whisper import WhisperModel

            logger.info(
                "whisper_model_loading",
                model_size=self._settings.whisper_model_size,
                device=self._settings.whisper_device,
            )
            self._model = WhisperModel(
                self._settings.whisper_model_size,
                device=self._settings.whisper_device,
                compute_type=self._settings.whisper_compute_type,
            )
        return self._model

    async def transcribe(self, audio_path: Path) -> str:
        if not audio_path.exists():
            raise TranscriptionError(f"Audio file not found: {audio_path}")

        try:
            import asyncio

            # faster-whisper's API is synchronous/CPU-bound; run it in a
            # worker thread so it doesn't block the event loop.
            return await asyncio.to_thread(self._transcribe_sync, audio_path)
        except TranscriptionError:
            raise
        except Exception as exc:  # noqa: BLE001 - wrap any whisper/ctranslate2 failure
            raise TranscriptionError(f"Transcription failed: {exc}") from exc

    def _transcribe_sync(self, audio_path: Path) -> str:
        model = self._get_model()
        segments, _info = model.transcribe(str(audio_path))
        text = " ".join(segment.text.strip() for segment in segments)
        if not text.strip():
            raise TranscriptionError("Transcription produced no text (silent or unsupported audio)")
        return text.strip()
