import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.document import Document
from app.models.user import User
from app.schemas.document import DocumentOut
from app.services.ingestion import process_document

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])

UPLOAD_DIR = Path("uploads")
ALLOWED_EXTENSIONS = {".pdf", ".txt"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


@router.post("/upload", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only .pdf and .txt files are allowed")

    contents = file.file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="File is empty")
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 5 MB)")

    UPLOAD_DIR.mkdir(exist_ok=True)
    doc_id = uuid.uuid4()
    save_path = UPLOAD_DIR / f"{doc_id}{suffix}"
    save_path.write_bytes(contents)

    document = Document(
        id=doc_id,
        user_id=current_user.id,
        filename=file.filename,
        content_type=file.content_type,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    try:
        chunk_count = process_document(db, doc_id, save_path)
        if chunk_count == 0:
            raise ValueError("No text could be extracted from this file")
    except Exception as exc:
        db.rollback()
        db.delete(document)
        db.commit()
        save_path.unlink(missing_ok=True)
        logger.exception("Document processing failed")
        if isinstance(exc, ValueError):
            raise HTTPException(status_code=422, detail=str(exc))
        raise HTTPException(status_code=500, detail="Failed to process document")

    return document