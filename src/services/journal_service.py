"""Journal entry service."""

from dataclasses import dataclass
from datetime import date

from src.models.journal import JournalEntry
from src.repositories.wellness_repository import WellnessRepository
from src.safety import SafetyService
from src.safety.crisis_detector import CrisisResult
from src.utils.validation import validate_journal


@dataclass
class JournalSaveResult:
    entry: JournalEntry
    crisis: CrisisResult


class JournalService:
    def __init__(self, repo: WellnessRepository, safety: SafetyService) -> None:
        self.repo = repo
        self.safety = safety

    def save_entry(
        self,
        user_id: int,
        content: str,
        entry_date: date | None = None,
    ) -> JournalSaveResult:
        from src.utils.dates import today

        validated = validate_journal(content)
        crisis = self.safety.check_text(validated.content)
        entry = self.repo.upsert_journal_entry(
            user_id=user_id,
            content=validated.content,
            crisis_flagged=crisis.is_crisis,
            entry_date=entry_date or today(),
        )
        return JournalSaveResult(entry=entry, crisis=crisis)

    def get_recent(self, user_id: int, since: date) -> list[JournalEntry]:
        return self.repo.get_journal_entries_since(user_id, since)
