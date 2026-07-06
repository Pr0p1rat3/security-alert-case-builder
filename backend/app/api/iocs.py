from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import require_analyst, require_viewer
from app.db.session import get_db
from app.models import IOC, User
from app.schemas.ioc import IOCEnrichmentRead, IOCRead, ManualIOCCreate
from app.services.audit import audit_log
from app.services.enrichment_service import enrich_ioc
from app.services.ioc_service import extract_and_store_iocs

router = APIRouter(tags=["iocs"])


@router.get("/cases/{case_id}/iocs", response_model=list[IOCRead])
def list_iocs(
    case_id: int, _: User = Depends(require_viewer), db: Session = Depends(get_db)
) -> list[IOC]:
    return list(
        db.scalars(
            select(IOC)
            .where(IOC.case_id == case_id)
            .options(selectinload(IOC.enrichments))
            .order_by(IOC.type, IOC.value)
        ).all()
    )


@router.post("/cases/{case_id}/iocs/extract", response_model=list[IOCRead])
def extract_iocs(
    case_id: int,
    payload: ManualIOCCreate | None = None,
    actor: User = Depends(require_analyst),
    db: Session = Depends(get_db),
) -> list[IOC]:
    if payload:
        ioc = IOC(
            case_id=case_id,
            type=payload.type,
            value=payload.value,
            raw_value=payload.raw_value or payload.value,
        )
        db.add(ioc)
        db.flush()
        iocs = [ioc]
    else:
        from app.models import Alert

        raw = "\n".join(db.scalars(select(Alert.raw_content).where(Alert.case_id == case_id)).all())
        iocs = extract_and_store_iocs(db, case_id, None, raw)
    audit_log(db, actor, "ioc.extracted", case_id=case_id, details={"count": len(iocs)})
    db.commit()
    return iocs


@router.post("/iocs/{ioc_id}/enrich", response_model=list[IOCEnrichmentRead])
def enrich_one(ioc_id: int, actor: User = Depends(require_analyst), db: Session = Depends(get_db)):
    ioc = db.get(IOC, ioc_id)
    if not ioc:
        raise HTTPException(status_code=404, detail="IOC not found")
    results = enrich_ioc(db, ioc)
    audit_log(
        db, actor, "ioc.enriched", case_id=ioc.case_id, entity_type="IOC", entity_id=str(ioc.id)
    )
    db.commit()
    return results


@router.post("/cases/{case_id}/iocs/enrich-all", response_model=list[IOCEnrichmentRead])
def enrich_all(case_id: int, actor: User = Depends(require_analyst), db: Session = Depends(get_db)):
    results = []
    for ioc in db.scalars(select(IOC).where(IOC.case_id == case_id)):
        results.extend(enrich_ioc(db, ioc))
    audit_log(db, actor, "ioc.enriched_all", case_id=case_id, details={"count": len(results)})
    db.commit()
    return results
