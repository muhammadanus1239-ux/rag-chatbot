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

router = APIRouter(prefix="/documents", tags=["documents"])

UPLOAD_DIR = Path("uploads")
ALLOWED_EXTENSIONS = {".pdf", ".txt"}


@router.post("/upload", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only .pdf and .txt files are allowed")

    UPLOAD_DIR.mkdir(exist_ok=True)
    doc_id = uuid.uuid4()
    save_path = UPLOAD_DIR / f"{doc_id}{suffix}"
    with open(save_path, "wb") as f:
        f.write(file.file.read())

    document = Document(
        id=doc_id,
        user_id=current_user.id,
        filename=file.filename,
        content_type=file.content_type,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    process_document(db, doc_id, save_path)
    return document