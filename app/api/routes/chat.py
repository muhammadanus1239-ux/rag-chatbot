from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.message import Message
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse, MessageOut
from app.services.llm import generate_answer
from app.services.retrieval import search_chunks

router = APIRouter(prefix="/chat", tags=["chat"])

NO_DOCS_ANSWER = "Mujhe aapke documents mein is sawal ka jawab nahi mila. Pehle koi document upload karein."


@router.post("", response_model=ChatResponse)
def chat(
    data: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    asked_at = datetime.now(timezone.utc)
    results = search_chunks(db, current_user.id, data.question, data.top_k)

    if results:
        try:
            answer = generate_answer(data.question, [r["content"] for r in results])
        except Exception:
            raise HTTPException(status_code=502, detail="LLM request failed, try again")
    else:
        answer = NO_DOCS_ANSWER

    sources = [
        {
            "document_id": str(r["document_id"]),
            "chunk_index": r["chunk_index"],
            "content": r["content"],
            "distance": r["distance"],
        }
        for r in results
    ]

    db.add(Message(user_id=current_user.id, role="user", content=data.question, created_at=asked_at))
    db.add(
        Message(
            user_id=current_user.id,
            role="assistant",
            content=answer,
            sources=sources,
            created_at=datetime.now(timezone.utc),
        )
    )
    db.commit()

    return {"answer": answer, "sources": sources}


@router.get("/history", response_model=list[MessageOut])
def history(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = (
        select(Message)
        .where(Message.user_id == current_user.id)
        .order_by(Message.created_at)
        .limit(limit)
    )
    return db.execute(stmt).scalars().all()