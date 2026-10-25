from __future__ import annotations

from pathlib import Path
from typing import Any

from src.ingestion.chunker import chunk_text
from src.ingestion.extractors import extract_text
from src.retrieval.embedder import Embedder
from src.retrieval.vector_index import VectorIndex
from src.security.filesystem_auth import FilesystemAuthorizer


class HybridRetriever:
    def __init__(self, authorizer: FilesystemAuthorizer, embedder: Embedder | None = None, index: VectorIndex | None = None, chunk_size: int = 500, overlap: int = 80, top_k: int = 5):
        self.authorizer = authorizer
        self.embedder = embedder or Embedder()
        self.index = index or VectorIndex()
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.top_k = top_k

    def index_file(self, path: str | Path) -> int:
        p = self.authorizer.validate(path)
        text = extract_text(p)
        chunks = chunk_text(text, self.chunk_size, self.overlap)
        if not chunks:
            return 0
        vecs = self.embedder.encode(chunks)
        metas = [{"path": str(p), "chunk_id": i, "text": c} for i, c in enumerate(chunks)]
        self.index.add(vecs, metas)
        return len(chunks)

    def index_authorized(self) -> int:
        total = 0
        for p in self.authorizer.list_allowed_files():
            try:
                total += self.index_file(p)
            except Exception:
                continue
        return total

    def search(self, query: str, k: int | None = None) -> list[dict[str, Any]]:
        k = k or self.top_k
        results: list[dict[str, Any]] = []
        # filename/metadata search
        q_lower = query.lower()
        for meta in self.index.metadata:
            if q_lower in Path(meta["path"]).name.lower():
                results.append({"path": meta["path"], "chunk_id": meta["chunk_id"], "text": meta["text"], "score": 1.0, "source": "filename"})
        # semantic
        vec = self.embedder.encode([query])
        for score, meta in self.index.search(vec, k=k):
            results.append({"path": meta["path"], "chunk_id": meta["chunk_id"], "text": meta["text"], "score": score, "source": "semantic"})
        # dedup by (path, chunk_id)
        seen = set()
        deduped = []
        for r in results:
            key = (r["path"], r["chunk_id"])
            if key in seen:
                continue
            seen.add(key)
            deduped.append(r)
        deduped.sort(key=lambda x: x["score"], reverse=True)
        return deduped[:k]

    def save(self, index_path: str, metadata_path: str):
        self.index.save(index_path, metadata_path)

    def load(self, index_path: str, metadata_path: str):
        self.index = VectorIndex.load(index_path, metadata_path)
