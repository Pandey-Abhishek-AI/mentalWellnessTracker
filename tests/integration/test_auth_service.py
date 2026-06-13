"""Authentication service tests."""

import pytest

from src.services.auth_service import AuthError, AuthService
from src.utils.uuids import uuid_from_email


@pytest.fixture
def auth_service(repo) -> AuthService:
    return AuthService(repo)


def test_register_creates_user_with_uuid(auth_service):
    result = auth_service.register("student@example.com", "password123")
    assert result.user.email == "student@example.com"
    assert result.user.user_uuid == uuid_from_email("student@example.com")


def test_register_rejects_duplicate_email(auth_service):
    auth_service.register("student@example.com", "password123")
    with pytest.raises(AuthError, match="already exists"):
        auth_service.register("student@example.com", "otherpass99")


def test_login_success(auth_service):
    auth_service.register("student@example.com", "password123")
    result = auth_service.login("student@example.com", "password123")
    assert result.user.email == "student@example.com"


def test_login_rejects_wrong_password(auth_service):
    auth_service.register("student@example.com", "password123")
    with pytest.raises(AuthError, match="Invalid email or password"):
        auth_service.login("student@example.com", "wrongpassword")
