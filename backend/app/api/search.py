from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.api.deps import require_viewer
from app.db.session import get_db
from app.models import IOC, Alert, Case, User

router = APIRouter(tags=["search"])


@router.get("/search")
def search(
    q: str, _: User = Depends(require_viewer), db: Session = Depends(get_db)
) -> dict[str, list[dict]]:
    pattern = f"%{q}%"
    cases = db.scalars(
        select(Case)
        .where(or_(Case.title.ilike(pattern), Case.description.ilike(pattern)))
        .limit(20)
    ).all()
    iocs = db.scalars(select(IOC).where(IOC.value.ilike(pattern)).limit(20)).all()
    alerts = db.scalars(select(Alert).where(Alert.raw_content.ilike(pattern)).limit(20)).all()
    return {
        "cases": [
            {
                "id": case.id,
                "title": case.title,
                "severity": case.severity.value,
                "status": case.status.value,
            }
            for case in cases
        ],
        "iocs": [
            {"id": ioc.id, "case_id": ioc.case_id, "type": ioc.type.value, "value": ioc.value}
            for ioc in iocs
        ],
        "alerts": [
            {"id": alert.id, "case_id": alert.case_id, "source_system": alert.source_system}
            for alert in alerts
        ],
    }
