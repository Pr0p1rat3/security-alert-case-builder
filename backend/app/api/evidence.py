from __future__ import annotations

import hashlib
import secrets
from datetime import UTC, datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_analyst, require_viewer
from app.core.config import get_settings
from app.db.session import get_db
from app.models import EvidenceFile, User
from app.schemas.evidence import EvidenceRead
from app.services.audit import audit_log

router = APIRouter(tags=["evidence"])

ALLOWED_EXTENSIONS = {".txt", ".csv", ".json", ".log", ".png", ".jpg", ".jpeg", ".pdf"}


@router.post("/cases/{case_id}/evidence", response_model=EvidenceRead)
async def upload_evidence(
    case_id: int,
    file: UploadFile = File(...),
    description: str | None = Form(None),
    actor: User = Depends(require_analyst),
    db: Session = Depends(get_db),
) -> EvidenceFile:
    settings = get_settings()
    extension = Path(file.filename or "").suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported evidence file type")
    data = await file.read()
    if len(data) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail="Evidence file too large")
    digest = hashlib.sha256(data).hexdigest()
    case_dir = settings.evidence_storage_path / str(case_id)
    case_dir.mkdir(parents=True, exist_ok=True)
    safe_name = f"{digest[:16]}-{secrets.token_hex(4)}{extension}"
    storage_path = case_dir / safe_name
    storage_path.write_bytes(data)
    record = EvidenceFile(
        case_id=case_id,
        file_name=file.filename or safe_name,
        storage_path=str(storage_path),
        content_type=file.content_type or "application/octet-stream",
        sha256=digest,
        size_bytes=len(data),
        uploaded_by_id=actor.id,
        description=description,
    )
    db.add(record)
    db.flush()
    audit_log(
        db,
        actor,
        "evidence.added",
        case_id=case_id,
        entity_type="EvidenceFile",
        entity_id=str(record.id),
    )
    db.commit()
    db.refresh(record)
    return record


@router.get("/cases/{case_id}/evidence", response_model=list[EvidenceRead])
def list_evidence(case_id: int, _: User = Depends(require_viewer), db: Session = Depends(get_db)):
    return list(
        db.scalars(
            select(EvidenceFile).where(
                EvidenceFile.case_id == case_id, EvidenceFile.deleted_at.is_(None)
            )
        ).all()
    )


@router.get("/evidence/{evidence_id}/download")
def download_evidence(
    evidence_id: int, _: User = Depends(require_viewer), db: Session = Depends(get_db)
) -> FileResponse:
    evidence = db.get(EvidenceFile, evidence_id)
    if not evidence or evidence.deleted_at:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return FileResponse(
        evidence.storage_path, filename=evidence.file_name, media_type=evidence.content_type
    )


@router.delete("/evidence/{evidence_id}")
def delete_evidence(
    evidence_id: int, actor: User = Depends(require_analyst), db: Session = Depends(get_db)
) -> dict[str, str]:
    evidence = db.get(EvidenceFile, evidence_id)
    if not evidence or evidence.deleted_at:
        raise HTTPException(status_code=404, detail="Evidence not found")
    evidence.deleted_at = datetime.now(UTC)
    audit_log(
        db,
        actor,
        "evidence.deleted",
        case_id=evidence.case_id,
        entity_type="EvidenceFile",
        entity_id=str(evidence.id),
    )
    db.commit()
    return {"message": "evidence soft-deleted"}
