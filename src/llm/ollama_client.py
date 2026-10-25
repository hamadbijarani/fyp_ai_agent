from __future__ import annotations

import json
import os
from typing import Any

try:
    import ollama
except Exception:  # optional dependency
    ollama = None

from src.config import load_settings
from src.llm.base import LLMClient


class OllamaClient(LLMClient):
    def __init__(self, model: str | None = None, base_url: str | None = None, temperature: float = 0.2, max_tokens: int = 512, timeout: int = 120):
        cfg = load_settings().get("llm", {})
        self.model = model or os.getenv("OLLAMA_MODEL") or cfg.get("model")
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL") or cfg.get("base_url")
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        if ollama is None:
            raise RuntimeError('ollama package not installed')
        self._client = ollama.Client(host=self.base_url, timeout=self.timeout)

    def generate(self, prompt: str, system: str | None = None, format_json: bool = False) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        opts = {"temperature": self.temperature, "num_predict": self.max_tokens}
        kwargs: dict[str, Any] = {"model": self.model, "messages": messages, "options": opts}
        if format_json:
            kwargs["format"] = "json"
        try:
            resp = self._client.chat(**kwargs)
            return resp["message"]["content"]
        except Exception as e:
            raise RuntimeError(f"Ollama generate failed: {e}") from e

    def generate_json(self, prompt: str, system: str | None = None) -> dict:
        raw = self.generate(prompt, system=system, format_json=True)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            # try to extract json
            start = raw.find("{")
            end = raw.rfind("}")
            if start != -1 and end != -1:
                return json.loads(raw[start : end + 1])
            raise
