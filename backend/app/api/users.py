from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.core.security import hash_password
from app.db.session import get_db
from app.models import User
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services.audit import audit_log

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserRead])
def list_users(_: User = Depends(require_admin), db: Session = Depends(get_db)) -> list[User]:
    return list(db.scalars(select(User).order_by(User.email)).all())


@router.post("", response_model=UserRead)
def create_user(
    payload: UserCreate, actor: User = Depends(require_admin), db: Session = Depends(get_db)
) -> User:
    if db.scalar(select(User).where(User.email == payload.email)):
        raise HTTPException(status_code=409, detail="User already exists")
    user = User(
        email=payload.email,
        display_name=payload.display_name,
        password_hash=hash_password(payload.password),
        role=payload.role,
        active=True,
    )
    db.add(user)
    db.flush()
    audit_log(
        db,
        actor,
        "user.created",
        entity_type="User",
        entity_id=str(user.id),
        details={"email": user.email},
    )
    db.commit()
    db.refresh(user)
    return user


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    payload: UserUpdate,
    actor: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> User:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    audit_log(
        db,
        actor,
        "user.updated",
        entity_type="User",
        entity_id=str(user.id),
        details=payload.model_dump(exclude_unset=True),
    )
    db.commit()
    db.refresh(user)
    return user
