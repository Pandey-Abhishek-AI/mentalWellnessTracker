"""Date utilities."""

from datetime import date, timedelta


def today() -> date:
    return date.today()


def days_ago(n: int) -> date:
    return today() - timedelta(days=n)
