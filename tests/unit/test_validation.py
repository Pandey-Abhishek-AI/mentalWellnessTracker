"""Unit tests for input validation."""

import pytest

from src.utils.validation import ValidationError, validate_journal, validate_scale


def test_validate_scale_valid():
    assert validate_scale(3, "Mood") == 3


def test_validate_scale_too_low():
    with pytest.raises(ValidationError):
        validate_scale(0, "Mood")


def test_validate_scale_too_high():
    with pytest.raises(ValidationError):
        validate_scale(6, "Energy")


def test_validate_journal_too_short():
    with pytest.raises(ValidationError):
        validate_journal("short")


def test_validate_journal_valid():
    result = validate_journal("Today was a long day of studying for NEET.")
    assert result.char_count >= 10


def test_validate_journal_strips_whitespace():
    result = validate_journal("   Today was stressful but I managed.   ")
    assert not result.content.startswith(" ")
