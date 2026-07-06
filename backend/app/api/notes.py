from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_analyst, require_viewer
from app.db.session import get_db
from app.models import Case, Note, User
from app.schemas.note import NoteCreate, NoteRead
from app.services.audit import audit_log

router = APIRouter(tags=["notes"])


@router.get("/cases/{case_id}/notes", response_model=list[NoteRead])
def list_notes(
    case_id: int, _: User = Depends(require_viewer), db: Session = Depends(get_db)
) -> list[Note]:
    case = db.get(Case, case_id)
    if not case or case.deleted_at:
        raise HTTPException(status_code=404, detail="Case not found")
    return list(
        db.scalars(
            select(Note).where(Note.case_id == case_id).order_by(Note.created_at.desc())
        ).all()
    )


@router.post("/cases/{case_id}/notes", response_model=NoteRead)
def create_note(
    case_id: int,
    payload: NoteCreate,
    actor: User = Depends(require_analyst),
    db: Session = Depends(get_db),
) -> Note:
    case = db.get(Case, case_id)
    if not case or case.deleted_at:
        raise HTTPException(status_code=404, detail="Case not found")
    note = Note(case_id=case_id, author_id=actor.id, body=payload.body)
    db.add(note)
    db.flush()
    audit_log(
        db, actor, "comment.added", case_id=case_id, entity_type="Note", entity_id=str(note.id)
    )
    db.commit()
    db.refresh(note)
    return note
