from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.core.rate_limit import check_login_rate_limit
from app.core.security import create_access_token, verify_password
from app.db.session import get_db
from app.models import User
from app.schemas.auth import LoginRequest, TokenResponse, UserMe
from app.services.audit import audit_log

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)) -> TokenResponse:
    check_login_rate_limit(request)
    user = db.scalar(select(User).where(User.email == payload.email, User.active.is_(True)))
    if not user or not verify_password(payload.password, user.password_hash):
        audit_log(db, None, "user.login_failed", details={"email": payload.email})
        db.commit()
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(user.email, user.role.value)
    audit_log(db, user, "user.login")
    db.commit()
    return TokenResponse(access_token=token)


@router.post("/logout")
def logout(user: User = Depends(current_user), db: Session = Depends(get_db)) -> dict[str, str]:
    audit_log(db, user, "user.logout")
    db.commit()
    return {"message": "logged out"}


@router.get("/me", response_model=UserMe)
def me(user: User = Depends(current_user)) -> UserMe:
    return UserMe(
        id=user.id, email=user.email, display_name=user.display_name, role=user.role.value
    )
