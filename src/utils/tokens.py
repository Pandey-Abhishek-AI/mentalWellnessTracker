"""Rough token estimation for chat budget enforcement."""


def estimate_tokens(text: str) -> int:
    """Conservative chars/4 estimate when provider token counts are unavailable."""
    if not text:
        return 0
    return max(1, len(text) // 4)
