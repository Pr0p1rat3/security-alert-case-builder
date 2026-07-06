from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.models.enums import CaseStatus, Severity
from app.schemas.common import ORMModel


class CaseCreate(BaseModel):
    title: str
    description: str = ""
    severity: Severity = Severity.medium
    source_system: str | None = None
    assigned_analyst_id: int | None = None
    business_impact: str | None = None


class CaseUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    severity: Severity | None = None
    status: CaseStatus | None = None
    assigned_analyst_id: int | None = None
    close_reason: str | None = None
    business_impact: str | None = None
    affected_users: str | None = None
    affected_hosts: str | None = None
    affected_ips: str | None = None
    affected_domains_urls: str | None = None


class CaseRead(ORMModel):
    id: int
    title: str
    description: str
    severity: Severity
    status: CaseStatus
    source_system: str | None
    created_by_id: int
    assigned_analyst_id: int | None
    created_at: datetime
    updated_at: datetime
    close_reason: str | None
    business_impact: str | None
    affected_users: str | None
    affected_hosts: str | None
    affected_ips: str | None
    affected_domains_urls: str | None
