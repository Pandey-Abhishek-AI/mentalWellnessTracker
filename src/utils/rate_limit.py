"""In-memory rate limiting for login attempts."""

from collections import defaultdict
from datetime import datetime, timedelta, timezone

_login_failures: dict[str, list[datetime]] = defaultdict(list)


def check_login_allowed(email: str, max_attempts: int, window_minutes: int) -> None:
    normalized = email.strip().lower()
    window = timedelta(minutes=window_minutes)
    now = datetime.now(timezone.utc)
    recent = [ts for ts in _login_failures[normalized] if now - ts < window]
    _login_failures[normalized] = recent
    if len(recent) >= max_attempts:
        raise ValueError(
            f"Too many login attempts. Try again in {window_minutes} minutes."
        )


def record_login_failure(email: str) -> None:
    _login_failures[email.strip().lower()].append(datetime.now(timezone.utc))


def clear_login_failures(email: str) -> None:
    _login_failures.pop(email.strip().lower(), None)
