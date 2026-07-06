from __future__ import annotations

from datetime import datetime

from app.schemas.common import ORMModel


class EvidenceRead(ORMModel):
    id: int
    case_id: int
    timeline_event_id: int | None
    file_name: str
    content_type: str
    sha256: str
    size_bytes: int
    uploaded_by_id: int
    uploaded_at: datetime
    description: str | None
