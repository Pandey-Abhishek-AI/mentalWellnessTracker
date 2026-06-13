"""Input validation utilities."""

from dataclasses import dataclass

from app.config import get_settings


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
