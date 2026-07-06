from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import ORMModel


class TimelineEventCreate(BaseModel):
    timestamp: datetime
    event_type: str
    source_system: str | None = None
    short_title: str
    description: str
    related_user: str | None = None
    related_host: str | None = None
    related_entity: str | None = None
    confidence: float = 0.7


class TimelineEventUpdate(BaseModel):
    timestamp: datetime | None = None
    event_type: str | None = None
    short_title: str | None = None
    description: str | None = None
    order_index: int | None = None


class TimelineEventRead(ORMModel):
    id: int
    case_id: int
    alert_id: int | None
    timestamp: datetime
    event_type: str
    source_system: str | None
    short_title: str
    description: str
    related_user: str | None
    related_host: str | None
    related_entity: str | None
    confidence: float
    order_index: int
