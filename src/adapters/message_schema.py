from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class Message(BaseModel):
    id: str
    source: Literal["email", "whatsapp"]
    sender: str
    timestamp: datetime
    subject: str | None = None
    body: str
    metadata: dict[str, Any] = Field(default_factory=dict)

    def normalized_text(self) -> str:
        parts = []
        if self.subject:
            parts.append(f"Subject: {self.subject}")
        parts.append(f"From: {self.sender}")
        parts.append(f"Date: {self.timestamp.isoformat()}")
        parts.append(self.body)
        return "\n".join(parts)
