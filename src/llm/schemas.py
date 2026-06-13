"""Pydantic schemas for LLM responses."""

from pydantic import BaseModel, Field


class InsightPayload(BaseModel):
    triggers: list[str] = Field(default_factory=list)
    patterns: list[str] = Field(default_factory=list)
    themes: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)


class ChatTurn(BaseModel):
    role: str
    content: str
