"""Google Gemini LLM client adapter with mock support."""

import json
import time
from typing import Protocol

import httpx

from app.config import get_settings
from src.llm.prompts import COPING_PROMPT, INSIGHT_PROMPT, SYSTEM_PROMPT
from src.llm.schemas import ChatTurn, InsightPayload
from src.utils.logging import logger

GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"


class LLMError(Exception):
    pass


class LLMClient(Protocol):
    def generate_insight(self, context: str, exam_type: str) -> InsightPayload: ...
    def chat(self, messages: list[ChatTurn], context: str, exam_type: str) -> str: ...
    def generate_coping(self, exercise_type: str, context: str, exam_type: str) -> str: ...


# Backward-compatible alias used across services/tests
GrokClient = LLMClient


class GeminiClient:
    """Google Gemini via Generative Language API."""

    def __init__(self) -> None:
        settings = get_settings()
        if not settings.llm_enabled:
            raise LLMError("GEMINI_API_KEY is not configured.")
        self.settings = settings

    def _call_with_retry(
        self,
        model: str,
        system: str,
        contents: list[dict],
        max_retries: int = 3,
    ) -> str:
        payload: dict = {
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": contents,
            "generationConfig": {"temperature": 0.7},
        }

        url = f"{GEMINI_API_BASE}/models/{model}:generateContent"
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.settings.gemini_api_key,
        }

        last_error: Exception | None = None
        for attempt in range(max_retries):
            try:
                with httpx.Client(timeout=self.settings.llm_timeout_seconds) as client:
                    response = client.post(url, headers=headers, json=payload)
                    response.raise_for_status()
                    data = response.json()
                candidates = data.get("candidates") or []
                if not candidates:
                    raise LLMError("Empty response from Gemini")
                parts = candidates[0].get("content", {}).get("parts") or []
                text = parts[0].get("text", "") if parts else ""
                if not text.strip():
                    raise LLMError("Empty response from Gemini")
                return text.strip()
            except Exception as exc:
                last_error = exc
                logger.warning(
                    "Gemini call failed (attempt %d): %s", attempt + 1, type(exc).__name__
                )
                if attempt < max_retries - 1:
                    time.sleep(2**attempt)
        raise LLMError(f"Gemini request failed after {max_retries} attempts: {last_error}")

    def generate_insight(self, context: str, exam_type: str) -> InsightPayload:
        prompt = INSIGHT_PROMPT.format(exam_type=exam_type, context=context)
        contents = [{"role": "user", "parts": [{"text": prompt}]}]
        raw = self._call_with_retry(self.settings.gemini_model_insight, SYSTEM_PROMPT, contents)
        try:
            json_str = raw
            if "```" in raw:
                json_str = raw.split("```")[1]
                if json_str.startswith("json"):
                    json_str = json_str[4:]
            data = json.loads(json_str.strip())
            return InsightPayload.model_validate(data)
        except (json.JSONDecodeError, ValueError) as exc:
            raise LLMError(f"Failed to parse insight JSON: {exc}") from exc

    def chat(self, messages: list[ChatTurn], context: str, exam_type: str) -> str:
        from src.llm.prompts import wrap_user_content

        system = SYSTEM_PROMPT + f"\nStudent is preparing for: {exam_type}."
        if context:
            system += f"\nRecent wellness context:\n{wrap_user_content(context)}"

        normalized = [
            ChatTurn(
                role=m.role,
                content=wrap_user_content(m.content) if m.role == "user" else m.content,
            )
            for m in messages
        ]
        contents = [
            {
                "role": "user" if turn.role == "user" else "model",
                "parts": [{"text": turn.content}],
            }
            for turn in normalized
        ]
        return self._call_with_retry(
            self.settings.gemini_model_chat,
            system,
            contents,
        )

    def generate_coping(self, exercise_type: str, context: str, exam_type: str) -> str:
        prompt = COPING_PROMPT.format(
            exercise_type=exercise_type,
            exam_type=exam_type,
            context=context or "General exam preparation stress.",
        )
        contents = [{"role": "user", "parts": [{"text": prompt}]}]
        return self._call_with_retry(self.settings.gemini_model_chat, SYSTEM_PROMPT, contents)


class MockLLMClient:
    """Mock client for testing without API calls."""

    def generate_insight(self, context: str, exam_type: str) -> InsightPayload:
        return InsightPayload(
            triggers=["Mock tests", "Sleep deprivation"],
            patterns=["Mood dips after mock tests", "Lower energy on weekdays"],
            themes=["Exam anxiety", "Self-doubt"],
            suggestions=["Take a 10-minute walk after study blocks", "Practice 4-7-8 breathing"],
        )

    def chat(self, messages: list[ChatTurn], context: str, exam_type: str) -> str:
        return (
            "I hear that exam prep can feel overwhelming. "
            "Remember that your worth is not defined by a single test score. "
            "Would you like to try a short breathing exercise?"
        )

    def generate_coping(self, exercise_type: str, context: str, exam_type: str) -> str:
        return (
            f"**{exercise_type.title()} for {exam_type} prep**\n\n"
            "1. Sit comfortably and close your eyes.\n"
            "2. Breathe in for 4 counts, hold for 4, exhale for 6.\n"
            "3. Repeat 5 times. Notice your shoulders relaxing.\n"
            "4. Return to study with a clearer mind."
        )


MockGrokClient = MockLLMClient
OpenAIGrokClient = GeminiClient  # legacy test import name


def get_llm_client(use_mock: bool = False) -> LLMClient:
    if use_mock:
        return MockLLMClient()
    settings = get_settings()
    if not settings.llm_enabled:
        return MockLLMClient()
    return GeminiClient()
