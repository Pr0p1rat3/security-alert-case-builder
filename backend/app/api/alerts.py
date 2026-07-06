from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_analyst, require_viewer
from app.db.session import get_db
from app.models import Alert, Case, Task, User
from app.parsers.alert_parser import parse_alert
from app.schemas.alert import AlertPaste, AlertRead
from app.services.audit import audit_log
from app.services.ioc_service import extract_and_store_iocs
from app.services.timeline_service import create_timeline_from_alert
from app.tasks.recommendations import recommend_tasks

router = APIRouter(tags=["alerts"])


@router.post("/cases/{case_id}/alerts/paste", response_model=AlertRead)
def paste_alert(
    case_id: int,
    payload: AlertPaste,
    actor: User = Depends(require_analyst),
    db: Session = Depends(get_db),
) -> Alert:
    return _create_alert(
        db, actor, case_id, payload.raw_content, payload.source_system, payload.alert_type
    )


@router.post("/cases/{case_id}/alerts/upload", response_model=AlertRead)
async def upload_alert(
    case_id: int,
    file: UploadFile = File(...),
    actor: User = Depends(require_analyst),
    db: Session = Depends(get_db),
) -> Alert:
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Alert upload too large")
    raw = content.decode("utf-8", errors="replace")
    filename = file.filename or "uploaded-alert.txt"
    alert_type = (
        "json" if filename.endswith(".json") else "csv" if filename.endswith(".csv") else "text"
    )
    return _create_alert(db, actor, case_id, raw, filename, alert_type)


@router.get("/cases/{case_id}/alerts", response_model=list[AlertRead])
def case_alerts(
    case_id: int, _: User = Depends(require_viewer), db: Session = Depends(get_db)
) -> list[Alert]:
    return list(
        db.scalars(
            select(Alert).where(Alert.case_id == case_id).order_by(Alert.created_at.desc())
        ).all()
    )


@router.get("/alerts/{alert_id}", response_model=AlertRead)
def get_alert(
    alert_id: int, _: User = Depends(require_viewer), db: Session = Depends(get_db)
) -> Alert:
    alert = db.get(Alert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


def _create_alert(
    db: Session, actor: User, case_id: int, raw: str, source: str | None, alert_type: str | None
) -> Alert:
    case = db.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    parsed = parse_alert(raw, alert_type)
    alert = Alert(
        case_id=case_id,
        source_system=source or case.source_system,
        alert_type=parsed.alert_type,
        raw_content=raw,
        parsed=parsed.fields,
        confidence=parsed.confidence,
    )
    db.add(alert)
    db.flush()
    extract_and_store_iocs(db, case_id, alert, raw)
    create_timeline_from_alert(db, alert)
    for title, description, priority in recommend_tasks(alert.alert_type, raw):
        db.add(Task(case_id=case_id, title=title, description=description, priority=priority))
    audit_log(
        db,
        actor,
        "alert.uploaded",
        case_id=case_id,
        entity_type="Alert",
        entity_id=str(alert.id),
        details={"source": source},
    )
    db.commit()
    db.refresh(alert)
    return alert
