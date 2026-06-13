"""Pytest configuration and fixtures."""

import pytest

from src.llm.client import MockGrokClient
from src.repositories.wellness_repository import WellnessRepository
from src.safety import SafetyService
from src.services.chat_service import ChatService
from src.services.insight_service import InsightService
from src.services.journal_service import JournalService
from src.services.mood_service import MoodService


@pytest.fixture
def repo() -> WellnessRepository:
    return WellnessRepository("sqlite:///:memory:")


@pytest.fixture
def safety() -> SafetyService:
    return SafetyService()


@pytest.fixture
def mock_llm() -> MockGrokClient:
    return MockGrokClient()


@pytest.fixture
def user_id(repo: WellnessRepository) -> int:
    return repo.get_or_create_default_user().id


@pytest.fixture
def mood_service(repo: WellnessRepository) -> MoodService:
    return MoodService(repo)


@pytest.fixture
def journal_service(repo: WellnessRepository, safety: SafetyService) -> JournalService:
    return JournalService(repo, safety)


@pytest.fixture
def insight_service(
    repo: WellnessRepository, safety: SafetyService, mock_llm: MockGrokClient
) -> InsightService:
    return InsightService(repo, safety, mock_llm)


@pytest.fixture
def chat_service(
    repo: WellnessRepository, safety: SafetyService, mock_llm: MockGrokClient
) -> ChatService:
    return ChatService(repo, safety, mock_llm)
