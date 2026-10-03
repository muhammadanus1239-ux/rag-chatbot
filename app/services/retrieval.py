import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.chunk import Chunk
from app.models.document import Document
from app.services.embeddings import embed_texts


def search_chunks(db: Session, user_id: uuid.UUID, question: str, top_k: int = 3):
    query_vector = embed_texts([question])[0]
    distance = Chunk.embedding.cosine_distance(query_vector)

    stmt = (
        select(Chunk, distance.label("distance"))
        .join(Document, Chunk.document_id == Document.id)
        .where(Document.user_id == user_id)
        .order_by(distance)
        .limit(top_k)
    )

    return [
        {
            "chunk_id": chunk.id,
            "document_id": chunk.document_id,
            "chunk_index": chunk.chunk_index,
            "content": chunk.content,
            "distance": float(dist),
        }
        for chunk, dist in db.execute(stmt).all()
    ]