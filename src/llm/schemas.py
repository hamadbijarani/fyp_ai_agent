from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ClassificationResult(BaseModel):
    intent: Literal["reply_needed", "info_request", "no_action", "urgent", "spam"]
    needs_reply: bool
    needs_file_context: bool
    missing_info: list[str] = Field(default_factory=list)
    confidence: float = 0.0
    rationale: str = ""


class DraftResult(BaseModel):
    subject: str | None = None
    body: str
    sources: list[str] = Field(default_factory=list)
    missing_info: list[str] = Field(default_factory=list)
    confidence: float = 0.0
