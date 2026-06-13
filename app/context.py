"""Shared app context and service wiring."""

from functools import lru_cache

from src.repositories.wellness_repository import WellnessRepository
from src.safety import SafetyService
from src.services.chat_service import ChatService
from src.services.coping_service import CopingService
from src.services.insight_service import InsightService
from src.services.journal_service import JournalService
from src.services.mood_service import MoodService
from src.voice.client import VoiceClient, get_voice_client


@lru_cache
def get_repository() -> WellnessRepository:
    return WellnessRepository()


@lru_cache
def get_safety() -> SafetyService:
    return SafetyService()


def get_mood_service() -> MoodService:
    return MoodService(get_repository())


def get_journal_service() -> JournalService:
    return JournalService(get_repository(), get_safety())


def get_insight_service() -> InsightService:
    return InsightService(get_repository(), get_safety())


def get_chat_service() -> ChatService:
    return ChatService(get_repository(), get_safety())


def get_coping_service() -> CopingService:
    return CopingService(get_repository(), get_safety())


@lru_cache
def get_voice_client_cached() -> VoiceClient:
    return get_voice_client()


def ensure_session_state() -> int:
    """Initialize Streamlit session state and return user_id."""
    import streamlit as st

    repo = get_repository()
    user = repo.get_or_create_default_user()

    defaults = {
        "user_id": user.id,
        "disclaimer_accepted": user.disclaimer_accepted_at is not None,
        "chat_turns": 0,
        "chat_messages": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    return st.session_state.user_id
