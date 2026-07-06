from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.models.enums import TaskStatus
from app.schemas.common import ORMModel


class TaskCreate(BaseModel):
    title: str
    description: str
    priority: str = "Medium"
    assigned_to_id: int | None = None
    due_date: datetime | None = None
    evidence_link: str | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    priority: str | None = None
    status: TaskStatus | None = None
    assigned_to_id: int | None = None
    completion_notes: str | None = None


class TaskRead(ORMModel):
    id: int
    case_id: int
    title: str
    description: str
    priority: str
    status: TaskStatus
    assigned_to_id: int | None
    due_date: datetime | None
    evidence_link: str | None
    completion_notes: str | None
