"""Safety service orchestrating crisis detection and output filtering."""

from src.safety.crisis_detector import CrisisResult, detect_crisis, filter_unsafe_output
from src.safety.disclaimers import CRISIS_MESSAGE, DISCLAIMER_TEXT, PRIVACY_NOTICE
from src.safety.helplines import Helpline, get_helplines


class SafetyService:
    def check_text(self, text: str) -> CrisisResult:
        return detect_crisis(text)

    def filter_llm_output(self, text: str) -> str:
        return filter_unsafe_output(text)

    def get_disclaimer(self) -> str:
        return DISCLAIMER_TEXT

    def get_privacy_notice(self) -> str:
        return PRIVACY_NOTICE

    def get_crisis_message(self) -> str:
        return CRISIS_MESSAGE

    def get_helplines(self) -> list[Helpline]:
        return get_helplines()

    def is_safe_for_llm(self, text: str) -> bool:
        return not detect_crisis(text).is_crisis
