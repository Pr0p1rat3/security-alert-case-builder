from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import require_viewer
from app.db.session import get_db
from app.models import IOC, Case, Task, User
from app.models.enums import Severity, TaskStatus
from app.schemas.common import DashboardSummary

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard/summary", response_model=DashboardSummary)
def dashboard(_: User = Depends(require_viewer), db: Session = Depends(get_db)) -> DashboardSummary:
    severity_rows = db.execute(
        select(Case.severity, func.count()).where(Case.deleted_at.is_(None)).group_by(Case.severity)
    ).all()
    status_rows = db.execute(
        select(Case.status, func.count()).where(Case.deleted_at.is_(None)).group_by(Case.status)
    ).all()
    recent = db.scalars(
        select(Case).where(Case.deleted_at.is_(None)).order_by(Case.created_at.desc()).limit(8)
    ).all()
    high = db.scalars(
        select(Case)
        .where(Case.severity.in_([Severity.high, Severity.critical]), Case.deleted_at.is_(None))
        .order_by(Case.created_at.desc())
        .limit(8)
    ).all()
    top_iocs = db.execute(
        select(IOC.value, func.count()).group_by(IOC.value).order_by(func.count().desc()).limit(10)
    ).all()
    backlog = (
        db.scalar(
            select(func.count())
            .select_from(Task)
            .where(Task.status.in_([TaskStatus.open, TaskStatus.in_progress, TaskStatus.blocked]))
        )
        or 0
    )
    return DashboardSummary(
        open_cases_by_severity={row[0].value: row[1] for row in severity_rows},
        cases_by_status={row[0].value: row[1] for row in status_rows},
        recently_created_cases=[
            {
                "id": case.id,
                "title": case.title,
                "severity": case.severity.value,
                "status": case.status.value,
            }
            for case in recent
        ],
        recent_high_cases=[
            {
                "id": case.id,
                "title": case.title,
                "severity": case.severity.value,
                "status": case.status.value,
            }
            for case in high
        ],
        top_iocs=[{"value": value, "count": count} for value, count in top_iocs],
        task_backlog=backlog,
    )
