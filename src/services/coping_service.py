"""Coping toolkit service."""

from dataclasses import dataclass

from src.llm.client import GrokClient, LLMError, get_llm_client
from src.repositories.wellness_repository import WellnessRepository
from src.safety import SafetyService
from src.safety.crisis_detector import CrisisResult
from src.utils.dates import days_ago


@dataclass
class CopingResult:
    content: str | None
    crisis: CrisisResult | None
    error: str | None


EXERCISE_TYPES = [
    "breathing exercise",
    "reframing prompt",
    "micro-break plan",
]


class CopingService:
    def __init__(
        self,
        repo: WellnessRepository,
        safety: SafetyService,
        llm: GrokClient | None = None,
    ) -> None:
        self.repo = repo
        self.safety = safety
        self.llm = llm or get_llm_client()

    def _build_context(self, user_id: int) -> str:
        since = days_ago(7)
        moods = self.repo.get_mood_entries_since(user_id, since)
        journals = self.repo.get_journal_entries_since(user_id, since)
        if not moods and not journals:
            return "No recent data. General exam preparation stress."
        parts = []
        if moods:
            latest = moods[0]
            parts.append(
                f"Latest mood: {latest.mood}/5, energy {latest.energy}/5, tags: {latest.tags}"
            )
        if journals:
            parts.append(f"Latest journal excerpt: {journals[0].content[:200]}")
        return " ".join(parts)

    def generate(self, user_id: int, exercise_type: str, user_context: str = "") -> CopingResult:
        if exercise_type not in EXERCISE_TYPES:
            return CopingResult(
                content=None,
                crisis=None,
                error=f"Invalid exercise type. Choose from: {', '.join(EXERCISE_TYPES)}",
            )

        check_text = user_context or self._build_context(user_id)
        crisis = self.safety.check_text(check_text)
        if crisis.is_crisis:
            return CopingResult(content=None, crisis=crisis, error=None)

        user = self.repo.get_user(user_id)
        exam_type = user.exam_type if user else "NEET"
        context = user_context or self._build_context(user_id)

        try:
            raw = self.llm.generate_coping(exercise_type, context, exam_type)
            content = self.safety.filter_llm_output(raw)
            return CopingResult(content=content, crisis=None, error=None)
        except LLMError as exc:
            return CopingResult(content=None, crisis=None, error=str(exc))
