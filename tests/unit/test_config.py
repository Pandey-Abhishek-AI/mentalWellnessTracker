"""Tests for Gemini API key configuration."""

from app.config import Settings


def test_llm_enabled_for_nonempty_gemini_key():
    settings = Settings(gemini_api_key="AQ.test-gemini-key-value")
    assert settings.llm_enabled is True


def test_llm_disabled_when_key_missing():
    settings = Settings(gemini_api_key="")
    assert settings.llm_enabled is False


def test_llm_disabled_when_key_whitespace_only():
    settings = Settings(gemini_api_key="   ")
    assert settings.llm_enabled is False
