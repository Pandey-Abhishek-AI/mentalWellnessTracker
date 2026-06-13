"""Unit tests for crisis detection."""

from src.safety.crisis_detector import detect_crisis, filter_unsafe_output


def test_detect_crisis_positive():
    result = detect_crisis("I want to kill myself, I can't take this anymore")
    assert result.is_crisis
    assert "self_harm" in result.matched_patterns


def test_detect_crisis_self_harm():
    result = detect_crisis("I've been thinking about self-harm after the mock test")
    assert result.is_crisis
    assert "self_injury" in result.matched_patterns


def test_detect_crisis_negative():
    result = detect_crisis("I'm stressed about NEET but managing with breaks")
    assert not result.is_crisis
    assert result.matched_patterns == []


def test_detect_crisis_empty():
    result = detect_crisis("")
    assert not result.is_crisis


def test_filter_unsafe_output_banned_phrase():
    output = filter_unsafe_output("You have depression and should take medication.")
    assert "not qualified to give medical advice" in output


def test_filter_unsafe_output_safe():
    text = "Try a 5-minute breathing exercise after your study block."
    assert filter_unsafe_output(text) == text
