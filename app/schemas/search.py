import uuid

from pydantic import BaseModel


class SearchResult(BaseModel):
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    chunk_index: int
    content: str
    distance: float