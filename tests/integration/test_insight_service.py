"""Integration tests for insight service."""

from datetime import date


def test_insight_requires_minimum_entries(insight_service, user_id):
    result = insight_service.generate(user_id)
    assert result.insight is None
    assert "at least" in (result.error or "").lower()


def test_insight_generates_with_enough_data(insight_service, user_id, repo):
    repo.upsert_mood_entry(user_id, 2, 3, 2, ["mock test"], date(2026, 6, 10))
    repo.upsert_journal_entry(
        user_id,
        "Felt anxious after today's mock test but pushed through.",
        False,
        date(2026, 6, 11),
    )
    result = insight_service.generate(user_id)
    assert result.insight is not None
    assert len(result.insight.triggers) > 0


def test_insight_blocks_crisis(insight_service, user_id, repo):
    repo.upsert_mood_entry(user_id, 1, 1, 1, [], date(2026, 6, 10))
    repo.upsert_journal_entry(
        user_id,
        "I want to kill myself and can't go on anymore with this prep.",
        True,
        date(2026, 6, 11),
    )
    result = insight_service.generate(user_id)
    assert result.crisis is not None
    assert result.crisis.is_crisis
    assert result.insight is None
