"""Unit tests for LLM schemas."""


from src.llm.schemas import InsightPayload


def test_insight_payload_valid():
    payload = InsightPayload(
        triggers=["mock tests"],
        patterns=["low mood after tests"],
        themes=["anxiety"],
        suggestions=["take breaks"],
    )
    assert len(payload.triggers) == 1


def test_insight_payload_defaults():
    payload = InsightPayload()
    assert payload.triggers == []


def test_insight_payload_from_dict():
    data = {
        "triggers": ["sleep"],
        "patterns": ["late nights"],
        "themes": ["burnout"],
        "suggestions": ["sleep earlier"],
    }
    payload = InsightPayload.model_validate(data)
    assert payload.themes == ["burnout"]
