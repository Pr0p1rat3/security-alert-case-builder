from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_admin, require_viewer
from app.db.session import get_db
from app.models import AuditLog, User
from app.schemas.common import AuditLogRead

router = APIRouter(tags=["audit"])


@router.get("/cases/{case_id}/audit", response_model=list[AuditLogRead])
def case_audit(case_id: int, _: User = Depends(require_viewer), db: Session = Depends(get_db)):
    return list(
        db.scalars(
            select(AuditLog).where(AuditLog.case_id == case_id).order_by(AuditLog.created_at.desc())
        ).all()
    )


@router.get("/audit", response_model=list[AuditLogRead])
def all_audit(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    return list(db.scalars(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(500)).all())
