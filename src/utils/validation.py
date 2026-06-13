"""Input validation utilities."""

import re
from dataclasses import dataclass

from app.config import get_settings

_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class ValidationError(Exception):
    pass


@dataclass(frozen=True)
class JournalValidation:
    content: str
    char_count: int


def validate_scale(value: int, field_name: str) -> int:
    if not isinstance(value, int) or value < 1 or value > 5:
        raise ValidationError(f"{field_name} must be between 1 and 5.")
    return value


def validate_journal(content: str) -> JournalValidation:
    settings = get_settings()
    stripped = content.strip()
    length = len(stripped)

    if length < settings.min_journal_chars:
        raise ValidationError(
            f"Journal must be at least {settings.min_journal_chars} characters "
            f"(currently {length})."
        )
    if length > settings.max_journal_chars:
        raise ValidationError(
            f"Journal must be at most {settings.max_journal_chars} characters "
            f"(currently {length})."
        )
    return JournalValidation(content=stripped, char_count=length)


def validate_email(email: str) -> str:
    normalized = email.strip().lower()
    if not normalized or not _EMAIL_PATTERN.match(normalized):
        raise ValidationError("Enter a valid email address.")
    if len(normalized) > 255:
        raise ValidationError("Email address is too long.")
    return normalized


def validate_password(password: str) -> str:
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters.")
    if len(password) > 128:
        raise ValidationError("Password is too long.")
    return password
