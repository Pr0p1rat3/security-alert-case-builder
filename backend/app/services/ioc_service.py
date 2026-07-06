from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import IOC, Alert
from app.parsers.ioc_extractor import extract_iocs


def extract_and_store_iocs(
    db: Session, case_id: int, alert: Alert | None, raw_text: str
) -> list[IOC]:
    stored: list[IOC] = []
    for extracted in extract_iocs(raw_text):
        existing = db.scalar(
            select(IOC).where(
                IOC.case_id == case_id,
                IOC.type == extracted.type,
                IOC.value == extracted.value,
            )
        )
        if existing:
            existing.last_seen = datetime.now(UTC)
            if alert and not existing.alert_id:
                existing.alert_id = alert.id
            stored.append(existing)
            continue
        ioc = IOC(
            case_id=case_id,
            alert_id=alert.id if alert else None,
            type=extracted.type,
            value=extracted.value,
            raw_value=extracted.raw_value,
        )
        db.add(ioc)
        stored.append(ioc)
    db.flush()
    return stored
