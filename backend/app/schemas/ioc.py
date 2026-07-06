from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.models.enums import IocType, Verdict
from app.schemas.common import ORMModel


class IOCEnrichmentRead(ORMModel):
    id: int
    ioc_id: int
    provider_name: str
    verdict: Verdict
    confidence: float
    summary: str
    raw_response: dict[str, Any]
    enriched_at: datetime


class IOCRead(ORMModel):
    id: int
    case_id: int
    alert_id: int | None
    type: IocType
    value: str
    raw_value: str
    first_seen: datetime
    last_seen: datetime
    enrichments: list[IOCEnrichmentRead] = Field(default_factory=list)


class ManualIOCCreate(BaseModel):
    type: IocType
    value: str
    raw_value: str | None = None
