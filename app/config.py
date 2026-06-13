"""Application configuration loaded from environment variables."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    xai_api_key: str = ""
    xai_model_chat: str = "grok-4.1-fast"
    xai_model_insight: str = "grok-4.1-fast"
    database_url: str = "sqlite:///./data/wellness.db"
    log_level: str = "INFO"
    min_journal_chars: int = 10
    max_journal_chars: int = 5000
    daily_chat_token_budget: int = 8000
    max_chat_turns: int = 5
    llm_timeout_seconds: int = 30
    elevenlabs_api_key: str = ""
    elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"
    elevenlabs_model: str = "eleven_multilingual_v2"
    voice_enabled: bool = True
    max_voice_chars: int = 2500

    exam_types: list[str] = Field(
        default_factory=lambda: ["NEET", "JEE", "CUET", "CAT", "GATE", "UPSC", "Board"]
    )
    mood_tags: list[str] = Field(
        default_factory=lambda: [
            "mock test",
            "family pressure",
            "burnout",
            "lonely",
            "exam anxiety",
            "low motivation",
        ]
    )

    @property
    def data_dir(self) -> Path:
        return Path("data")

    @property
    def llm_enabled(self) -> bool:
        return bool(self.xai_api_key.strip())

    @property
    def voice_available(self) -> bool:
        return self.voice_enabled and bool(self.elevenlabs_api_key.strip())


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    return settings
