from pathlib import Path

from pypdf import PdfReader
from sqlalchemy.orm import Session

from app.models.chunk import Chunk
from app.services.embeddings import embed_texts


def extract_text(file_path: str | Path) -> str:
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".txt":
        return path.read_text(encoding="utf-8", errors="ignore")

    if suffix == ".pdf":
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    raise ValueError(f"Unsupported file type: {suffix}")


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    text = text.strip()
    chunks = []
    start = 0
    step = chunk_size - overlap

    while start < len(text):
        chunk = text[start : start + chunk_size].strip()
        if chunk:
            chunks.append(chunk)
        start += step

    return chunks


def process_document(db: Session, document_id, file_path: str | Path) -> int:
    text = extract_text(file_path)
    chunks = chunk_text(text)
    vectors = embed_texts(chunks)

    rows = [
        Chunk(
            document_id=document_id,
            chunk_index=index,
            content=content,
            embedding=vector,
        )
        for index, (content, vector) in enumerate(zip(chunks, vectors))
    ]
    db.add_all(rows)
    db.commit()
    return len(rows)