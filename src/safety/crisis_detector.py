"""Crisis language detection for user-generated text."""

import re
from dataclasses import dataclass

# Pattern names only — matched text is not logged (SEC-007).
CRISIS_PATTERNS: dict[str, re.Pattern[str]] = {
    "self_harm": re.compile(
        r"\b(kill\s+myself|end\s+my\s+life|want\s+to\s+die|suicide|suicidal)\b",
        re.IGNORECASE,
    ),
    "self_injury": re.compile(
        r"\b(self[\s-]?harm|cut\s+myself|hurt\s+myself|harm\s+myself)\b",
        re.IGNORECASE,
    ),
    "hopelessness": re.compile(
        r"\b(no\s+reason\s+to\s+live|better\s+off\s+dead|can'?t\s+go\s+on|give\s+up\s+on\s+life)\b",
        re.IGNORECASE,
    ),
    "method_mention": re.compile(
        r"\b(overdose|jump\s+off|hang\s+myself|slit\s+my\s+wrists)\b",
        re.IGNORECASE,
    ),
}

BANNED_ADVICE_PHRASES: list[str] = [
    "you should take medication",
    "stop taking your medication",
    "you have depression",
    "you have anxiety disorder",
    "diagnosed with",
    "no need to seek help",
    "suicide is",
    "just get over it",
]


@dataclass(frozen=True)
class CrisisResult:
    is_crisis: bool
    matched_patterns: list[str]


def detect_crisis(text: str) -> CrisisResult:
    if not text or not text.strip():
        return CrisisResult(is_crisis=False, matched_patterns=[])

    matched = [name for name, pattern in CRISIS_PATTERNS.items() if pattern.search(text)]
    return CrisisResult(is_crisis=bool(matched), matched_patterns=matched)


def filter_unsafe_output(text: str) -> str:
    """Remove or replace banned advice phrases from LLM output."""
    if not text:
        return text

    result = text
    for phrase in BANNED_ADVICE_PHRASES:
        if phrase.lower() in result.lower():
            result = (
                "I want to support you, but I'm not qualified to give medical advice. "
                "Please speak with a counselor or mental health professional. "
                "If you're in crisis, use the helplines shown on this page."
            )
            break
    return result
