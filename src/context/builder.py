from __future__ import annotations

from src.adapters.message_schema import Message
from src.llm.schemas import ClassificationResult
from src.retrieval.hybrid import HybridRetriever
from src.security.sanitizer import sanitize_text


class ContextBuilder:
    def __init__(self, retriever: HybridRetriever, max_chars: int = 4000):
        self.retriever = retriever
        self.max_chars = max_chars

    def build(self, message: Message, classification: ClassificationResult) -> tuple[str, list[str]]:
        if not classification.needs_file_context:
            return "", []
        query = message.body
        if message.subject:
            query = message.subject + "\n" + query
        hits = self.retriever.search(query)
        sources = []
        parts = []
        total = 0
        for h in hits:
            src = f"{h['path']}#chunk{h['chunk_id']}"
            if src not in sources:
                sources.append(src)
            text = sanitize_text(h["text"])
            if total + len(text) > self.max_chars:
                break
            parts.append(f"[{src}]\n{text}")
            total += len(text)
        return "\n\n".join(parts), sources
