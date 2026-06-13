"""Pytest configuration and fixtures."""

import pytest

from src.llm.client import MockGrokClient
from src.repositories.wellness_repository import WellnessRepository
from src.safety import SafetyService
from src.services.auth_service import AuthService
from src.services.chat_service import ChatService
from src.services.insight_service import InsightService
from src.services.journal_service import JournalService
from src.services.mood_service import MoodService


@pytest.fixture
def repo() -> WellnessRepository:
    return WellnessRepository("sqlite:///:memory:")


@pytest.fixture
def auth_service(repo: WellnessRepository) -> AuthService:
    return AuthService(repo)


@pytest.fixture
def safety() -> SafetyService:
    return SafetyService()


@pytest.fixture
def mock_llm() -> MockGrokClient:
    return MockGrokClient()


@pytest.fixture
def test_user(auth_service: AuthService):
    return auth_service.register("test@example.com", "password123").user


@pytest.fixture
def user_id(test_user) -> int:
    return test_user.id


@pytest.fixture
def user_uuid(test_user) -> str:
    return test_user.user_uuid


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
