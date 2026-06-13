"""Mood check-in service."""

from datetime import date

from src.models.mood import MoodEntry
from src.repositories.wellness_repository import WellnessRepository
from src.utils.validation import validate_scale


class MoodService:
    def __init__(self, repo: WellnessRepository) -> None:
        self.repo = repo

    def save_checkin(
        self,
        user_id: int,
        mood: int,
        energy: int,
        sleep_quality: int,
        tags: list[str],
        entry_date: date | None = None,
    ) -> MoodEntry:
        from src.utils.dates import today

        validate_scale(mood, "Mood")
        validate_scale(energy, "Energy")
        validate_scale(sleep_quality, "Sleep quality")
        return self.repo.upsert_mood_entry(
            user_id=user_id,
            mood=mood,
            energy=energy,
            sleep_quality=sleep_quality,
            tags=tags,
            entry_date=entry_date or today(),
        )

    def get_recent(self, user_id: int, since: date) -> list[MoodEntry]:
        return self.repo.get_mood_entries_since(user_id, since)
