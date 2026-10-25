from src.ingestion.chunker import chunk_text


def test_chunk_empty():
    assert chunk_text("") == []
    assert chunk_text("   ") == []


def test_chunk_basic():
    text = "a" * 100
    chunks = chunk_text(text, chunk_size=30, overlap=5)
    assert len(chunks) > 1
    assert all(len(c) <= 30 for c in chunks)


def test_chunk_overlap_covers():
    text = "abcdefghijklmnopqrstuvwxyz" * 4
    chunks = chunk_text(text, chunk_size=20, overlap=5)
    # reconstructed coverage
    assert chunks[0] == text[:20]
