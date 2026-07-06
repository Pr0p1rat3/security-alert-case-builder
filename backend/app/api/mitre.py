from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import require_analyst, require_viewer
from app.db.session import get_db
from app.mitre.engine import suggest_techniques
from app.models import Alert, CaseTechniqueMapping, MITRETechnique, User
from app.schemas.mitre import CaseTechniqueMappingRead, MappingUpdate
from app.services.audit import audit_log

router = APIRouter(tags=["mitre"])


@router.get("/cases/{case_id}/mitre", response_model=list[CaseTechniqueMappingRead])
def list_mitre(case_id: int, _: User = Depends(require_viewer), db: Session = Depends(get_db)):
    return list(
        db.scalars(
            select(CaseTechniqueMapping)
            .where(CaseTechniqueMapping.case_id == case_id)
            .options(selectinload(CaseTechniqueMapping.technique))
        ).all()
    )


@router.post("/cases/{case_id}/mitre/suggest", response_model=list[CaseTechniqueMappingRead])
def suggest_mitre(
    case_id: int, actor: User = Depends(require_analyst), db: Session = Depends(get_db)
):
    text = "\n".join(db.scalars(select(Alert.raw_content).where(Alert.case_id == case_id)).all())
    mappings = []
    for suggestion in suggest_techniques(text):
        technique = db.scalar(
            select(MITRETechnique).where(MITRETechnique.technique_id == suggestion["technique_id"])
        )
        if not technique:
            continue
        existing = db.scalar(
            select(CaseTechniqueMapping).where(
                CaseTechniqueMapping.case_id == case_id,
                CaseTechniqueMapping.technique_id == technique.id,
            )
        )
        if existing:
            mappings.append(existing)
            continue
        mapping = CaseTechniqueMapping(
            case_id=case_id,
            technique_id=technique.id,
            why_suggested=str(suggestion["why_suggested"]),
            confidence=float(suggestion["confidence"]),
            related_evidence="Suggested from alert text.",
        )
        db.add(mapping)
        mappings.append(mapping)
    audit_log(db, actor, "mitre.suggested", case_id=case_id, details={"count": len(mappings)})
    mapping_ids = [mapping.id for mapping in mappings]
    db.commit()
    return list(
        db.scalars(
            select(CaseTechniqueMapping)
            .where(CaseTechniqueMapping.id.in_(mapping_ids))
            .options(selectinload(CaseTechniqueMapping.technique))
        ).all()
    )


@router.patch("/case-techniques/{mapping_id}", response_model=CaseTechniqueMappingRead)
def update_mapping(
    mapping_id: int,
    payload: MappingUpdate,
    actor: User = Depends(require_analyst),
    db: Session = Depends(get_db),
):
    mapping = db.get(CaseTechniqueMapping, mapping_id)
    if not mapping:
        raise HTTPException(status_code=404, detail="Mapping not found")
    mapping.analyst_status = payload.analyst_status
    audit_log(
        db,
        actor,
        "mitre.mapping_updated",
        case_id=mapping.case_id,
        entity_type="CaseTechniqueMapping",
        entity_id=str(mapping.id),
    )
    mapping_id = mapping.id
    db.commit()
    updated = db.scalar(
        select(CaseTechniqueMapping)
        .where(CaseTechniqueMapping.id == mapping_id)
        .options(selectinload(CaseTechniqueMapping.technique))
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Mapping not found")
    return updated
