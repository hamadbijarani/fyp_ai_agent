from __future__ import annotations

from typing import List

import numpy as np


class Embedder:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", device: str = "cpu"):
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(model_name, device=device)

    def encode(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, 384), dtype="float32")
        vecs = self.model.encode(texts, normalize_embeddings=True, convert_to_numpy=True)
        return vecs.astype("float32")
