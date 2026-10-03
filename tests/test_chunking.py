import pytest

from app.services.ingestion import chunk_text


def test_chunk_text_splits_long_text():
    chunks = chunk_text("a" * 100, chunk_size=30, overlap=5)
    assert len(chunks) > 1
    assert all(len(c) <= 30 for c in chunks)


def test_chunk_text_empty_text_gives_no_chunks():
    assert chunk_text("   ") == []


def test_chunk_text_rejects_bad_overlap():
    with pytest.raises(ValueError):
        chunk_text("hello", chunk_size=10, overlap=10)