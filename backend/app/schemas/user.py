from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import UserRole
from app.schemas.common import ORMModel


class UserCreate(BaseModel):
    email: EmailStr
    display_name: str
    password: str = Field(min_length=12, max_length=512)
    role: UserRole = UserRole.viewer


class UserUpdate(BaseModel):
    display_name: str | None = None
    role: UserRole | None = None
    active: bool | None = None


class UserRead(ORMModel):
    id: int
    email: EmailStr
    display_name: str
    role: UserRole
    active: bool
    created_at: datetime
