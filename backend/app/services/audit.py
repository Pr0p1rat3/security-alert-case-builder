from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.models import AuditLog, User

SENSITIVE_KEYS = {"password", "token", "secret", "authorization", "api_key", "apikey"}


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: (
                "[REDACTED]"
                if any(marker in key.lower() for marker in SENSITIVE_KEYS)
                else redact(item)
            )
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value


def audit_log(
    db: Session,
    actor: User | None,
    action: str,
    case_id: int | None = None,
    entity_type: str | None = None,
    entity_id: str | None = None,
    details: dict[str, Any] | None = None,
) -> AuditLog:
    event = AuditLog(
        actor_id=actor.id if actor else None,
        case_id=case_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=redact(details or {}),
    )
    db.add(event)
    db.flush()
    return event
