"""Unit tests for prompt utilities."""

from src.llm.prompts import build_chat_messages, wrap_user_content


def test_wrap_user_content():
    result = wrap_user_content("hello world")
    assert "<user_content>" in result
    assert "hello world" in result


def test_build_chat_messages_includes_system():
    messages = build_chat_messages("system prompt", "context", [], "user msg")
    assert messages[0]["role"] == "system"
    assert any(m["role"] == "user" for m in messages)
