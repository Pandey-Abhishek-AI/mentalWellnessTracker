"""Integration tests for wellness repository."""

from datetime import date

from src.repositories.wellness_repository import WellnessRepository


def test_create_user(repo: WellnessRepository):
    user = repo.create_user(
        email="solo@example.com",
        user_uuid="00000000-0000-4000-8000-000000000001",
        password_hash="hash",
        password_salt="salt",
    )
    assert user.email == "solo@example.com"


def test_upsert_mood_entry(repo: WellnessRepository, user_id: int):
    entry = repo.upsert_mood_entry(
        user_id=user_id,
        mood=3,
        energy=4,
        sleep_quality=2,
        tags=["mock test"],
        entry_date=date(2026, 6, 1),
    )
    assert entry.mood == 3

    updated = repo.upsert_mood_entry(
        user_id=user_id,
        mood=2,
        energy=3,
        sleep_quality=2,
        tags=[],
        entry_date=date(2026, 6, 1),
    )
    assert updated.id == entry.id
    assert updated.mood == 2


def test_upsert_journal_entry(repo: WellnessRepository, user_id: int):
    entry = repo.upsert_journal_entry(
        user_id=user_id,
        content="Today was a hard day of JEE prep.",
        crisis_flagged=False,
        entry_date=date(2026, 6, 1),
    )
    assert entry.crisis_flagged is False


def test_save_and_get_insight(repo: WellnessRepository, user_id: int):
    insight = repo.save_insight(
        user_id=user_id,
        summary_json={"triggers": ["tests"], "patterns": [], "themes": [], "suggestions": []},
        period_start=date(2026, 5, 1),
        period_end=date(2026, 6, 1),
    )
    latest = repo.get_latest_insight(user_id)
    assert latest is not None
    assert latest.id == insight.id


def test_clear_user_data(repo: WellnessRepository, user_id: int):
    repo.upsert_mood_entry(user_id, 3, 3, 3, [], date(2026, 6, 1))
    repo.upsert_journal_entry(user_id, "journal entry text here.", False, date(2026, 6, 1))
    repo.clear_user_data(user_id)
    moods = repo.get_mood_entries_since(user_id, date(2000, 1, 1))
    assert len(moods) == 0
