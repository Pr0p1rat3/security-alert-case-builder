from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Message(BaseModel):
    message: str


class DashboardSummary(BaseModel):
    open_cases_by_severity: dict[str, int]
    cases_by_status: dict[str, int]
    recently_created_cases: list[dict[str, Any]]
    recent_high_cases: list[dict[str, Any]]
    top_iocs: list[dict[str, Any]]
    task_backlog: int


class AuditLogRead(ORMModel):
    id: int
    actor_id: int | None
    case_id: int | None
    action: str
    entity_type: str | None
    entity_id: str | None
    details: dict[str, Any]
    created_at: datetime
