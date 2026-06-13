"""Companion chat service."""

from dataclasses import dataclass

from app.config import get_settings
from src.llm.client import LLMClient, LLMError, get_llm_client
from src.llm.schemas import ChatTurn
from src.models.chat import ChatMessage
from src.repositories.wellness_repository import WellnessRepository
from src.safety import SafetyService
from src.safety.crisis_detector import CrisisResult
from src.utils.dates import days_ago, start_of_today_utc
from src.utils.tokens import estimate_tokens


@dataclass
class ChatResult:
    message: str | None
    crisis: CrisisResult | None
    error: str | None
    turns_remaining: int


class ChatService:
    def __init__(
        self,
        repo: WellnessRepository,
        safety: SafetyService,
        llm: LLMClient | None = None,
    ) -> None:
        self.repo = repo
        self.safety = safety
        self.llm = llm or get_llm_client()
        self.settings = get_settings()

    def _build_context(self, user_id: int) -> str:
        since = days_ago(7)
        moods = self.repo.get_mood_entries_since(user_id, since)
        journals = self.repo.get_journal_entries_since(user_id, since)
        lines: list[str] = []
        for m in moods[:5]:
            lines.append(f"Mood {m.entry_date}: {m.mood}/5, energy {m.energy}/5")
        for j in journals[:3]:
            preview = j.content[:200]
            lines.append(f"Journal {j.entry_date}: {preview}")
        return "\n".join(lines)

    def send_message(
        self,
        user_id: int,
        user_message: str,
        session_turns: int,
        session_history: list[ChatTurn],
    ) -> ChatResult:
        max_turns = self.settings.max_chat_turns
        turns_remaining = max_turns - session_turns

        if turns_remaining <= 0:
            return ChatResult(
                message=None,
                crisis=None,
                error=f"Session limit reached ({max_turns} messages). Start a new session.",
                turns_remaining=0,
            )

        budget = self.settings.daily_chat_token_budget
        user = self.repo.get_user(user_id)
        user_uuid = user.user_uuid if user else None
        if not user_uuid:
            return ChatResult(
                message=None,
                crisis=None,
                error="Account UUID missing. Please log out and sign in again.",
                turns_remaining=turns_remaining,
            )

        used_today = self.repo.estimate_chat_tokens_since_uuid(user_uuid, start_of_today_utc())
        reserved = estimate_tokens(user_message) + 400
        if used_today + reserved > budget:
            return ChatResult(
                message=None,
                crisis=None,
                error=(
                    f"Daily chat token budget reached for your account "
                    f"({budget} estimated tokens). Try again tomorrow UTC."
                ),
                turns_remaining=turns_remaining,
            )

        crisis = self.safety.check_text(user_message)
        self.repo.save_chat_message(
            user_id, "user", user_message, crisis_flagged=crisis.is_crisis
        )

        if crisis.is_crisis:
            return ChatResult(
                message=None,
                crisis=crisis,
                error=None,
                turns_remaining=turns_remaining,
            )

        exam_type = user.exam_type if user else "NEET"
        context = self._build_context(user_id)

        history = session_history + [ChatTurn(role="user", content=user_message)]

        try:
            raw_response = self.llm.chat(history, context, exam_type)
            response = self.safety.filter_llm_output(raw_response)
            self.repo.save_chat_message(user_id, "assistant", response)
            return ChatResult(
                message=response,
                crisis=None,
                error=None,
                turns_remaining=turns_remaining - 1,
            )
        except LLMError as exc:
            return ChatResult(
                message=None,
                crisis=None,
                error=str(exc),
                turns_remaining=turns_remaining,
            )

    def get_history(self, user_id: int, limit: int = 20) -> list[ChatMessage]:
        return list(reversed(self.repo.get_chat_history(user_id, limit)))
