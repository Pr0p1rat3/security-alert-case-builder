from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import ORMModel


class ReportGenerate(BaseModel):
    report_type: str = "analyst"
    format: str = "markdown"


class ReportRead(ORMModel):
    id: int
    case_id: int
    report_type: str
    format: str
    content: str
    created_by_id: int
    created_at: datetime
