from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.schemas.common import ORMModel


class AlertPaste(BaseModel):
    raw_content: str
    source_system: str | None = None
    alert_type: str | None = None


class AlertRead(ORMModel):
    id: int
    case_id: int
    source_system: str | None
    alert_type: str
    raw_content: str
    parsed: dict[str, Any]
    confidence: float
    created_at: datetime
