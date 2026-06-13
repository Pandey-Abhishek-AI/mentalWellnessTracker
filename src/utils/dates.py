"""Date utilities."""

from datetime import date, datetime, timedelta, timezone


def today() -> date:
    return date.today()


def days_ago(n: int) -> date:
    return today() - timedelta(days=n)


def start_of_today_utc() -> datetime:
    return datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
