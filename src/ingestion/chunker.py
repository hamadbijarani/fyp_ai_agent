from __future__ import annotations


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 80) -> list[str]:
    text = text.strip()
    if not text:
        return []
    if chunk_size <= 0:
        return [text]
    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        chunks.append(text[start:end])
        if end >= n:
            break
        start = max(end - overlap, start + 1)
    return chunks
