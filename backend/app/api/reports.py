from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import require_analyst, require_viewer
from app.db.session import get_db
from app.models import Case, Report, User
from app.models.mitre import CaseTechniqueMapping
from app.reports.generator import generate_html, generate_markdown
from app.schemas.report import ReportGenerate, ReportRead
from app.services.audit import audit_log

router = APIRouter(tags=["reports"])


@router.post("/cases/{case_id}/reports/generate", response_model=ReportRead)
def generate_report(
    case_id: int,
    payload: ReportGenerate,
    actor: User = Depends(require_analyst),
    db: Session = Depends(get_db),
) -> Report:
    case = db.scalar(
        select(Case)
        .where(Case.id == case_id)
        .options(
            selectinload(Case.iocs),
            selectinload(Case.timeline_events),
            selectinload(Case.tasks),
            selectinload(Case.evidence),
            selectinload(Case.alerts),
            selectinload(Case.technique_mappings).selectinload(CaseTechniqueMapping.technique),
        )
    )
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    markdown = generate_markdown(case, payload.report_type)
    content = generate_html(markdown) if payload.format == "html" else markdown
    report = Report(
        case_id=case_id,
        report_type=payload.report_type,
        format=payload.format,
        content=content,
        created_by_id=actor.id,
    )
    db.add(report)
    db.flush()
    audit_log(
        db,
        actor,
        "report.generated",
        case_id=case_id,
        entity_type="Report",
        entity_id=str(report.id),
        details={"type": payload.report_type},
    )
    db.commit()
    db.refresh(report)
    return report


@router.get("/cases/{case_id}/reports", response_model=list[ReportRead])
def list_reports(case_id: int, _: User = Depends(require_viewer), db: Session = Depends(get_db)):
    return list(
        db.scalars(
            select(Report).where(Report.case_id == case_id).order_by(Report.created_at.desc())
        ).all()
    )


@router.get("/reports/{report_id}", response_model=ReportRead)
def get_report(
    report_id: int, _: User = Depends(require_viewer), db: Session = Depends(get_db)
) -> Report:
    report = db.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report
