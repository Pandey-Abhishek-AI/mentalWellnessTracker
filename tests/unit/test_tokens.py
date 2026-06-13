"""Tests for token estimation utilities."""

from src.utils.tokens import estimate_tokens


def test_estimate_tokens_empty():
    assert estimate_tokens("") == 0


def test_estimate_tokens_short_text():
    assert estimate_tokens("hello") >= 1


def test_estimate_tokens_scales_with_length():
    short = estimate_tokens("a" * 40)
    long = estimate_tokens("a" * 400)
    assert long > short
