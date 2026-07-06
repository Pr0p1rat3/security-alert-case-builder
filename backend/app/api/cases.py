from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import require_admin, require_analyst, require_viewer
from app.db.session import get_db
from app.models import Case, User
from app.schemas.case import CaseCreate, CaseRead, CaseUpdate
from app.services.audit import audit_log

router = APIRouter(prefix="/cases", tags=["cases"])


@router.get("", response_model=list[CaseRead])
def list_cases(_: User = Depends(require_viewer), db: Session = Depends(get_db)) -> list[Case]:
    return list(
        db.scalars(
            select(Case).where(Case.deleted_at.is_(None)).order_by(Case.updated_at.desc())
        ).all()
    )


@router.post("", response_model=CaseRead)
def create_case(
    payload: CaseCreate, actor: User = Depends(require_analyst), db: Session = Depends(get_db)
) -> Case:
    case = Case(**payload.model_dump(), created_by_id=actor.id)
    db.add(case)
    db.flush()
    audit_log(
        db, actor, "case.created", case_id=case.id, entity_type="Case", entity_id=str(case.id)
    )
    db.commit()
    db.refresh(case)
    return case


@router.get("/{case_id}", response_model=CaseRead)
def get_case(
    case_id: int, _: User = Depends(require_viewer), db: Session = Depends(get_db)
) -> Case:
    case = db.scalar(
        select(Case)
        .where(Case.id == case_id, Case.deleted_at.is_(None))
        .options(selectinload(Case.iocs))
    )
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@router.patch("/{case_id}", response_model=CaseRead)
def update_case(
    case_id: int,
    payload: CaseUpdate,
    actor: User = Depends(require_analyst),
    db: Session = Depends(get_db),
) -> Case:
    case = db.get(Case, case_id)
    if not case or case.deleted_at:
        raise HTTPException(status_code=404, detail="Case not found")
    old = {"severity": case.severity.value, "status": case.status.value}
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(case, field, value)
    audit_log(
        db,
        actor,
        "case.updated",
        case_id=case.id,
        entity_type="Case",
        entity_id=str(case.id),
        details={"old": old, "new": payload.model_dump(exclude_unset=True)},
    )
    if payload.severity:
        audit_log(
            db,
            actor,
            "case.severity_changed",
            case_id=case.id,
            entity_type="Case",
            entity_id=str(case.id),
        )
    if payload.status:
        audit_log(
            db,
            actor,
            "case.status_changed",
            case_id=case.id,
            entity_type="Case",
            entity_id=str(case.id),
        )
    db.commit()
    db.refresh(case)
    return case


@router.delete("/{case_id}")
def delete_case(
    case_id: int, actor: User = Depends(require_admin), db: Session = Depends(get_db)
) -> dict[str, str]:
    case = db.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    case.deleted_at = datetime.now(UTC)
    audit_log(
        db, actor, "case.deleted", case_id=case.id, entity_type="Case", entity_id=str(case.id)
    )
    db.commit()
    return {"message": "case soft-deleted"}
