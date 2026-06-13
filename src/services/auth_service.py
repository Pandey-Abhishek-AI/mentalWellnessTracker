"""Authentication service for email login."""

from dataclasses import dataclass

from app.config import get_settings
from src.models.user import User
from src.repositories.wellness_repository import WellnessRepository
from src.utils.passwords import hash_password, verify_password
from src.utils.rate_limit import (
    check_login_allowed,
    clear_login_failures,
    record_login_failure,
)
from src.utils.uuids import uuid_from_email
from src.utils.validation import ValidationError, validate_email, validate_password


class AuthError(Exception):
    pass


@dataclass(frozen=True)
class AuthResult:
    user: User


class AuthService:
    def __init__(self, repo: WellnessRepository) -> None:
        self.repo = repo

    def register(self, email: str, password: str) -> AuthResult:
        try:
            normalized_email = validate_email(email)
            valid_password = validate_password(password)
        except ValidationError as exc:
            raise AuthError(str(exc)) from exc

        if self.repo.get_user_by_email(normalized_email) is not None:
            raise AuthError("An account with this email already exists. Please log in.")

        user_uuid = uuid_from_email(normalized_email)
        password_digest, salt = hash_password(valid_password)
        user = self.repo.create_user(
            email=normalized_email,
            user_uuid=user_uuid,
            password_hash=password_digest,
            password_salt=salt,
        )
        return AuthResult(user=user)

    def login(self, email: str, password: str) -> AuthResult:
        settings = get_settings()
        try:
            normalized_email = validate_email(email)
            valid_password = validate_password(password)
        except ValidationError as exc:
            raise AuthError(str(exc)) from exc

        try:
            check_login_allowed(
                normalized_email,
                settings.login_max_attempts,
                settings.login_lockout_minutes,
            )
        except ValueError as exc:
            raise AuthError(str(exc)) from exc

        user = self.repo.get_user_by_email(normalized_email)
        if user is None or not user.password_hash or not user.password_salt:
            record_login_failure(normalized_email)
            raise AuthError("Invalid email or password.")

        if not verify_password(valid_password, user.password_hash, user.password_salt):
            record_login_failure(normalized_email)
            raise AuthError("Invalid email or password.")

        expected_uuid = uuid_from_email(normalized_email)
        if user.user_uuid != expected_uuid:
            raise AuthError("Account identity mismatch. Contact support.")

        clear_login_failures(normalized_email)
        return AuthResult(user=user)
