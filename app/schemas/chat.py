import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    question: str = Field(min_length=1)
    top_k: int = Field(3, ge=1, le=10)


class SourceOut(BaseModel):
    document_id: uuid.UUID
    chunk_index: int
    content: str
    distance: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceOut]


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    role: str
    content: str
    sources: list[SourceOut] | None
    created_at: datetime