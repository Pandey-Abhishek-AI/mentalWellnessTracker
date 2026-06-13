"""Tests for ElevenLabs voice client."""

from unittest.mock import MagicMock, patch

import httpx
import pytest

from src.voice.client import (
    ElevenLabsVoiceClient,
    MockVoiceClient,
    VoiceError,
    plain_text_for_speech,
)


def test_plain_text_for_speech_strips_markdown():
    text = "**Hello** — try `breathing` and [help](https://example.com)."
    assert plain_text_for_speech(text) == "Hello — try breathing and help."


def test_mock_voice_client_returns_setup_message():
    result = MockVoiceClient().synthesize("Hello there.")
    assert result.audio is None
    assert "ELEVENLABS_API_KEY" in (result.error or "")


def test_elevenlabs_client_requires_api_key(monkeypatch):
    monkeypatch.setenv("ELEVENLABS_API_KEY", "")
    from app.config import get_settings

    get_settings.cache_clear()
    with pytest.raises(VoiceError):
        ElevenLabsVoiceClient()
    get_settings.cache_clear()


@patch("src.voice.client.get_settings")
def test_elevenlabs_client_synthesize_success(mock_get_settings):
    settings = MagicMock()
    settings.voice_available = True
    settings.elevenlabs_api_key = "test-key"
    settings.elevenlabs_voice_id = "voice-id"
    settings.elevenlabs_model = "eleven_multilingual_v2"
    settings.max_voice_chars = 2500
    settings.llm_timeout_seconds = 30
    mock_get_settings.return_value = settings

    mock_response = MagicMock()
    mock_response.content = b"fake-audio"
    mock_response.raise_for_status = MagicMock()

    mock_http = MagicMock()
    mock_http.post.return_value = mock_response
    mock_http.__enter__ = MagicMock(return_value=mock_http)
    mock_http.__exit__ = MagicMock(return_value=False)

    with patch("src.voice.client.httpx.Client", return_value=mock_http):
        result = ElevenLabsVoiceClient().synthesize("Take a deep breath.")

    assert result.audio == b"fake-audio"
    assert result.error is None


@patch("src.voice.client.get_settings")
def test_elevenlabs_client_synthesize_http_error(mock_get_settings):
    settings = MagicMock()
    settings.voice_available = True
    settings.elevenlabs_api_key = "test-key"
    settings.elevenlabs_voice_id = "voice-id"
    settings.elevenlabs_model = "eleven_multilingual_v2"
    settings.max_voice_chars = 2500
    settings.llm_timeout_seconds = 30
    mock_get_settings.return_value = settings

    request = httpx.Request("POST", "https://api.elevenlabs.io/v1/text-to-speech/voice-id")
    response = httpx.Response(401, request=request)
    error = httpx.HTTPStatusError("Unauthorized", request=request, response=response)

    mock_http = MagicMock()
    mock_http.post.side_effect = error
    mock_http.__enter__ = MagicMock(return_value=mock_http)
    mock_http.__exit__ = MagicMock(return_value=False)

    with patch("src.voice.client.httpx.Client", return_value=mock_http):
        result = ElevenLabsVoiceClient().synthesize("Hello.")

    assert result.audio is None
    assert result.error is not None
