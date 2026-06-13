"""AI insight generation service."""

from dataclasses import dataclass
from datetime import date

from src.llm.client import GrokClient, LLMError, get_llm_client
from src.llm.schemas import InsightPayload
from src.models.insight import Insight
from src.repositories.wellness_repository import WellnessRepository
from src.safety import SafetyService
from src.safety.crisis_detector import CrisisResult
from src.utils.dates import days_ago, today


@dataclass
class InsightResult:
    insight: InsightPayload | None
    crisis: CrisisResult | None
    cached: bool
    error: str | None
    entry_count: int


class InsightService:
    MIN_ENTRIES = 2
    LOOKBACK_DAYS = 7

    def __init__(
        self,
        repo: WellnessRepository,
        safety: SafetyService,
        llm: GrokClient | None = None,
    ) -> None:
        self.repo = repo
        self.safety = safety
        self.llm = llm or get_llm_client()

    def _build_context(self, user_id: int, since: date) -> tuple[str, int]:
        moods = self.repo.get_mood_entries_since(user_id, since)
        journals = self.repo.get_journal_entries_since(user_id, since)
        entry_count = len(moods) + len(journals)

        lines: list[str] = []
        for m in moods:
            lines.append(
                f"Date {m.entry_date}: mood={m.mood}, energy={m.energy}, "
                f"sleep={m.sleep_quality}, tags={m.tags}"
            )
        for j in journals:
            preview = j.content[:300] + ("..." if len(j.content) > 300 else "")
            lines.append(f"Date {j.entry_date} journal: {preview}")

        return "\n".join(lines), entry_count

    def generate(self, user_id: int) -> InsightResult:
        since = days_ago(self.LOOKBACK_DAYS)
        context, entry_count = self._build_context(user_id, since)

        if entry_count < self.MIN_ENTRIES:
            return InsightResult(
                insight=None,
                crisis=None,
                cached=False,
                error=(
                    f"Log at least {self.MIN_ENTRIES} mood or journal entries "
                    "to unlock insights."
                ),
                entry_count=entry_count,
            )

        crisis = self.safety.check_text(context)
        if crisis.is_crisis:
            return InsightResult(
                insight=None,
                crisis=crisis,
                cached=False,
                error=None,
                entry_count=entry_count,
            )

        user = self.repo.get_user(user_id)
        exam_type = user.exam_type if user else "NEET"

        try:
            payload = self.llm.generate_insight(context, exam_type)
            filtered_suggestions = [
                self.safety.filter_llm_output(s) for s in payload.suggestions
            ]
            payload = InsightPayload(
                triggers=payload.triggers,
                patterns=payload.patterns,
                themes=payload.themes,
                suggestions=filtered_suggestions,
            )
            self.repo.save_insight(
                user_id=user_id,
                summary_json=payload.model_dump(),
                period_start=since,
                period_end=today(),
            )
            return InsightResult(
                insight=payload,
                crisis=None,
                cached=False,
                error=None,
                entry_count=entry_count,
            )
        except LLMError as exc:
            cached_insight = self.repo.get_latest_insight(user_id)
            if cached_insight:
                payload = InsightPayload.model_validate(cached_insight.summary_json)
                return InsightResult(
                    insight=payload,
                    crisis=None,
                    cached=True,
                    error=str(exc),
                    entry_count=entry_count,
                )
            return InsightResult(
                insight=None,
                crisis=None,
                cached=False,
                error=str(exc),
                entry_count=entry_count,
            )

    def get_latest(self, user_id: int) -> Insight | None:
        return self.repo.get_latest_insight(user_id)
