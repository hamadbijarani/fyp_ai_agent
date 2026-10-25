from __future__ import annotations

from pydantic import ValidationError

from src.adapters.message_schema import Message
from src.llm.ollama_client import OllamaClient
from src.llm.prompts import CLASSIFICATION_SYSTEM, CLASSIFICATION_USER
from src.llm.schemas import ClassificationResult


class IntentClassifier:
    def __init__(self, client=None):
        self.client = client or OllamaClient()

    def classify(self, message: Message) -> ClassificationResult:
        prompt = CLASSIFICATION_USER.format(message=message.normalized_text())
        try:
            data = self.client.generate_json(prompt, system=CLASSIFICATION_SYSTEM)
            return ClassificationResult.model_validate(data)
        except (ValidationError, Exception) as e:
            return ClassificationResult(
                intent="no_action",
                needs_reply=False,
                needs_file_context=False,
                missing_info=[],
                confidence=0.0,
                rationale=f"classification_failed: {e}",
            )
