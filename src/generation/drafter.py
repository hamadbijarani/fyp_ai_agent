from __future__ import annotations

from src.adapters.message_schema import Message
from src.context.builder import ContextBuilder
from src.llm.ollama_client import OllamaClient
from src.llm.prompts import DRAFT_SYSTEM, DRAFT_USER
from src.llm.schemas import ClassificationResult, DraftResult


class Drafter:
    def __init__(self, client=None, context_builder: ContextBuilder | None = None):
        self.client = client or OllamaClient()
        self.context_builder = context_builder

    def draft(self, message: Message, classification: ClassificationResult, context: str | None = None, sources: list[str] | None = None) -> DraftResult:
        if context is None and self.context_builder is not None:
            context, sources = self.context_builder.build(message, classification)
        context = context or ""
        sources = sources or []
        prompt = DRAFT_USER.format(message=message.normalized_text(), context=context)
        try:
            data = self.client.generate_json(prompt, system=DRAFT_SYSTEM)
            data.setdefault("sources", sources)
            return DraftResult.model_validate(data)
        except Exception as e:
            return DraftResult(
                subject=message.subject,
                body=f"(draft generation failed: {e})",
                sources=sources,
                missing_info=classification.missing_info,
                confidence=0.0,
            )
