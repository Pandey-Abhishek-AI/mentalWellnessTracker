"""Grok LLM client adapter with mock support."""

import json
import time
from typing import Protocol

from openai import OpenAI

from app.config import get_settings
from src.llm.prompts import COPING_PROMPT, INSIGHT_PROMPT, SYSTEM_PROMPT
from src.llm.schemas import ChatTurn, InsightPayload
from src.utils.logging import logger


class LLMError(Exception):
    pass


class GrokClient(Protocol):
    def generate_insight(self, context: str, exam_type: str) -> InsightPayload: ...
    def chat(self, messages: list[ChatTurn], context: str, exam_type: str) -> str: ...
    def generate_coping(self, exercise_type: str, context: str, exam_type: str) -> str: ...


class OpenAIGrokClient:
    """OpenAI-compatible client for xAI Grok API."""

    def __init__(self) -> None:
        settings = get_settings()
        if not settings.llm_enabled:
            raise LLMError("XAI_API_KEY is not configured.")
        self.settings = settings
        self.client = OpenAI(
            api_key=settings.xai_api_key,
            base_url="https://api.x.ai/v1",
            timeout=settings.llm_timeout_seconds,
        )

    def _call_with_retry(self, model: str, messages: list[dict], max_retries: int = 3) -> str:
        last_error: Exception | None = None
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.7,
                )
                content = response.choices[0].message.content
                if not content:
                    raise LLMError("Empty response from LLM")
                return content.strip()
            except Exception as exc:
                last_error = exc
                logger.warning("LLM call failed (attempt %d): %s", attempt + 1, type(exc).__name__)
                if attempt < max_retries - 1:
                    time.sleep(2**attempt)
        raise LLMError(f"LLM request failed after {max_retries} attempts: {last_error}")

    def generate_insight(self, context: str, exam_type: str) -> InsightPayload:
        prompt = INSIGHT_PROMPT.format(exam_type=exam_type, context=context)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]
        raw = self._call_with_retry(self.settings.xai_model_insight, messages)
        try:
            # Extract JSON from response (handle markdown code blocks)
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

        api_messages: list[dict] = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT + f"\nStudent is preparing for: {exam_type}.",
            },
        ]
        if context:
            api_messages.append({
                "role": "system",
                "content": f"Recent wellness context:\n{wrap_user_content(context)}",
            })
        for m in messages:
            content = wrap_user_content(m.content) if m.role == "user" else m.content
            api_messages.append({"role": m.role, "content": content})
        return self._call_with_retry(self.settings.xai_model_chat, api_messages)

    def generate_coping(self, exercise_type: str, context: str, exam_type: str) -> str:
        prompt = COPING_PROMPT.format(
            exercise_type=exercise_type,
            exam_type=exam_type,
            context=context or "General exam preparation stress.",
        )
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]
        return self._call_with_retry(self.settings.xai_model_chat, messages)


class MockGrokClient:
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


def get_llm_client(use_mock: bool = False) -> GrokClient:
    if use_mock:
        return MockGrokClient()
    settings = get_settings()
    if not settings.llm_enabled:
        return MockGrokClient()
    return OpenAIGrokClient()
