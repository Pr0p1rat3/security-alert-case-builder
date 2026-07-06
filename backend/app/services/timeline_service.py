from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import Alert, TimelineEvent
from app.parsers.alert_parser import parse_timestamp


def create_timeline_from_alert(db: Session, alert: Alert) -> TimelineEvent:
    parsed = alert.parsed or {}
    title = (
        parsed.get("signature")
        or parsed.get("rule_name")
        or parsed.get("process_name")
        or alert.alert_type
    )
    related = (
        parsed.get("source_ip") or parsed.get("domain") or parsed.get("url") or parsed.get("sha256")
    )
    event = TimelineEvent(
        case_id=alert.case_id,
        alert_id=alert.id,
        timestamp=parse_timestamp(parsed.get("timestamp")),
        event_type=alert.alert_type,
        source_system=alert.source_system,
        short_title=str(title)[:300],
        description=str(parsed.get("raw_message") or alert.raw_content)[:5000],
        related_user=parsed.get("username"),
        related_host=parsed.get("hostname"),
        related_entity=related,
        confidence=alert.confidence,
    )
    db.add(event)
    db.flush()
    return event
