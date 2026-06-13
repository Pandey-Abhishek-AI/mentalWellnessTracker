"""Integration tests for chat service."""



def test_chat_responds_normally(chat_service, user_id):
    result = chat_service.send_message(
        user_id=user_id,
        user_message="I'm feeling stressed about tomorrow's mock test.",
        session_turns=0,
        session_history=[],
    )
    assert result.message is not None
    assert result.crisis is None


def test_chat_blocks_crisis(chat_service, user_id):
    result = chat_service.send_message(
        user_id=user_id,
        user_message="I want to end my life.",
        session_turns=0,
        session_history=[],
    )
    assert result.crisis is not None
    assert result.crisis.is_crisis
    assert result.message is None


def test_chat_enforces_turn_limit(chat_service, user_id):
    result = chat_service.send_message(
        user_id=user_id,
        user_message="Hello",
        session_turns=5,
        session_history=[],
    )
    assert result.message is None
    assert "limit" in (result.error or "").lower()


def test_chat_enforces_daily_token_budget(chat_service, user_id, user_uuid, repo):
    chat_service.settings.daily_chat_token_budget = 10
    repo.save_chat_message(user_id, "user", "x" * 200, crisis_flagged=False)
    result = chat_service.send_message(
        user_id=user_id,
        user_message="Another long stressed message about exams.",
        session_turns=0,
        session_history=[],
    )
    assert result.message is None
    assert "token budget" in (result.error or "").lower()
    assert user_uuid
