from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class NoteCreate(BaseModel):
    body: str = Field(min_length=1, max_length=20_000)


class NoteRead(ORMModel):
    id: int
    case_id: int
    author_id: int
    body: str
    created_at: datetime
