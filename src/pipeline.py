from __future__ import annotations

from src.adapters.message_schema import Message
from src.context.builder import ContextBuilder
from src.generation.drafter import Drafter
from src.intent.classifier import IntentClassifier
from src.llm.schemas import ClassificationResult, DraftResult
from src.storage.audit_log import AuditLog


class Pipeline:
    def __init__(self, classifier=None, context_builder=None, drafter=None, audit=None):
        self.classifier = classifier or IntentClassifier()
        self.context_builder = context_builder
        self.drafter = drafter or Drafter(context_builder=context_builder)
        self.audit = audit or AuditLog()

    def process(self, message: Message) -> dict:
        self.audit.record("message_detected", {"id": message.id, "source": message.source})
        classification: ClassificationResult = self.classifier.classify(message)
        self.audit.record("classified", {"intent": classification.intent, "needs_file_context": classification.needs_file_context})

        context = ""
        sources: list[str] = []
        if classification.needs_file_context and self.context_builder is not None:
            context, sources = self.context_builder.build(message, classification)
            if sources:
                self.audit.record("file_accessed", {"sources": sources})

        draft: DraftResult = self.drafter.draft(message, classification, context=context, sources=sources)
        self.audit.record("draft_created", {"sources": draft.sources, "missing_info": draft.missing_info})
        return {"message": message, "classification": classification, "context": context, "sources": sources, "draft": draft}
