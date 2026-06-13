"""Tests for email-derived UUIDs."""

from src.utils.uuids import uuid_from_email


def test_uuid_from_email_is_stable():
    assert uuid_from_email("Student@Example.com") == uuid_from_email("student@example.com")


def test_uuid_from_email_differs_by_email():
    assert uuid_from_email("a@example.com") != uuid_from_email("b@example.com")
