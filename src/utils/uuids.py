"""Deterministic user UUID derived from email."""

import uuid


def uuid_from_email(email: str) -> str:
    """Return a stable UUID string for a normalized email address."""
    normalized = email.strip().lower()
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, normalized))
