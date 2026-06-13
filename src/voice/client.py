"""ElevenLabs text-to-speech client for chat responses."""

import re
from dataclasses import dataclass
from typing import Protocol

import httpx

from app.config import get_settings
from src.utils.logging import logger

ELEVENLABS_TTS_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"


class VoiceError(Exception):
    pass


@dataclass
class VoiceResult:
    audio: bytes | None
    error: str | None = None


class VoiceClient(Protocol):
    def synthesize(self, text: str) -> VoiceResult: ...


def plain_text_for_speech(text: str) -> str:
    """Strip markdown so TTS reads naturally."""
    cleaned = text
    cleaned = re.sub(r"\*\*(.+?)\*\*", r"\1", cleaned)
    cleaned = re.sub(r"\*(.+?)\*", r"\1", cleaned)
    cleaned = re.sub(r"`(.+?)`", r"\1", cleaned)
    cleaned = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", cleaned)
    cleaned = re.sub(r"#{1,6}\s*", "", cleaned)
    return cleaned.strip()


class ElevenLabsVoiceClient:
    """ElevenLabs TTS via REST API."""

    def __init__(self) -> None:
        settings = get_settings()
        if not settings.voice_available:
            raise VoiceError("ELEVENLABS_API_KEY is not configured.")
        self.settings = settings

    def synthesize(self, text: str) -> VoiceResult:
        speech_text = plain_text_for_speech(text)
        if not speech_text:
            return VoiceResult(audio=None, error="Nothing to read aloud.")

        if len(speech_text) > self.settings.max_voice_chars:
            speech_text = speech_text[: self.settings.max_voice_chars].rsplit(" ", 1)[0] + "..."

        url = ELEVENLABS_TTS_URL.format(voice_id=self.settings.elevenlabs_voice_id)
        headers = {
            "xi-api-key": self.settings.elevenlabs_api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        }
        payload = {
            "text": speech_text,
            "model_id": self.settings.elevenlabs_model,
        }

        try:
            with httpx.Client(timeout=self.settings.llm_timeout_seconds) as client:
                response = client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                return VoiceResult(audio=response.content)
        except httpx.HTTPStatusError as exc:
            logger.warning("ElevenLabs TTS failed: HTTP %s", exc.response.status_code)
            return VoiceResult(audio=None, error="Voice playback is unavailable right now.")
        except httpx.HTTPError as exc:
            logger.warning("ElevenLabs TTS request failed: %s", type(exc).__name__)
            return VoiceResult(audio=None, error="Could not reach the voice service.")


class MockVoiceClient:
    """Fallback when ElevenLabs is not configured."""

    def synthesize(self, text: str) -> VoiceResult:
        return VoiceResult(
            audio=None,
            error="Add ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID to .env to hear responses.",
        )


def get_voice_client() -> VoiceClient:
    settings = get_settings()
    if settings.voice_available:
        return ElevenLabsVoiceClient()
    return MockVoiceClient()
