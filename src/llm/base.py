from __future__ import annotations

from abc import ABC, abstractmethod


class LLMClient(ABC):
    @abstractmethod
    def generate(self, prompt: str, system: str | None = None, format_json: bool = False) -> str:
        ...
