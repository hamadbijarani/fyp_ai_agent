from __future__ import annotations

import json
from pathlib import Path

import faiss
import numpy as np


class VectorIndex:
    def __init__(self, dim: int = 384):
        self.dim = dim
        self.index = faiss.IndexFlatIP(dim)
        self.metadata: list[dict] = []

    def add(self, vectors: np.ndarray, metas: list[dict]):
        if len(vectors) == 0:
            return
        self.index.add(vectors)
        self.metadata.extend(metas)

    def search(self, query_vec: np.ndarray, k: int = 5) -> list[tuple[float, dict]]:
        if self.index.ntotal == 0:
            return []
        k = min(k, self.index.ntotal)
        scores, idxs = self.index.search(query_vec.reshape(1, -1), k)
        out = []
        for score, idx in zip(scores[0], idxs[0]):
            if idx < 0:
                continue
            out.append((float(score), self.metadata[idx]))
        return out

    def save(self, index_path: str, metadata_path: str):
        Path(index_path).parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, index_path)
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f)

    @classmethod
    def load(cls, index_path: str, metadata_path: str, dim: int = 384) -> "VectorIndex":
        obj = cls(dim=dim)
        if Path(index_path).exists():
            obj.index = faiss.read_index(index_path)
        if Path(metadata_path).exists():
            with open(metadata_path, "r", encoding="utf-8") as f:
                obj.metadata = json.load(f)
        return obj
