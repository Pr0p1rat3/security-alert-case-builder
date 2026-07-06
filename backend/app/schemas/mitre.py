from __future__ import annotations

from app.models.enums import MappingStatus
from app.schemas.common import ORMModel


class TechniqueRead(ORMModel):
    id: int
    technique_id: str
    technique_name: str
    tactic: str
    description: str | None


class MappingUpdate(ORMModel):
    analyst_status: MappingStatus


class CaseTechniqueMappingRead(ORMModel):
    id: int
    case_id: int
    technique_id: int
    technique: TechniqueRead | None = None
    why_suggested: str
    confidence: float
    related_evidence: str | None
    analyst_status: MappingStatus
