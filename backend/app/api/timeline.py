from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_analyst, require_viewer
from app.db.session import get_db
from app.models import TimelineEvent, User
from app.schemas.timeline import TimelineEventCreate, TimelineEventRead, TimelineEventUpdate
from app.services.audit import audit_log

router = APIRouter(tags=["timeline"])


@router.get("/cases/{case_id}/timeline", response_model=list[TimelineEventRead])
def list_timeline(
    case_id: int,
    sort: str = "asc",
    entity: str | None = None,
    source_system: str | None = None,
    event_type: str | None = None,
    _: User = Depends(require_viewer),
    db: Session = Depends(get_db),
):
    stmt = select(TimelineEvent).where(TimelineEvent.case_id == case_id)
    if entity:
        stmt = stmt.where(TimelineEvent.related_entity.contains(entity))
    if source_system:
        stmt = stmt.where(TimelineEvent.source_system == source_system)
    if event_type:
        stmt = stmt.where(TimelineEvent.event_type == event_type)
    stmt = stmt.order_by(
        TimelineEvent.timestamp.desc() if sort == "desc" else TimelineEvent.timestamp.asc()
    )
    return list(db.scalars(stmt).all())


@router.post("/cases/{case_id}/timeline", response_model=TimelineEventRead)
def create_timeline(
    case_id: int,
    payload: TimelineEventCreate,
    actor: User = Depends(require_analyst),
    db: Session = Depends(get_db),
) -> TimelineEvent:
    event = TimelineEvent(case_id=case_id, **payload.model_dump())
    db.add(event)
    db.flush()
    audit_log(
        db,
        actor,
        "timeline.created",
        case_id=case_id,
        entity_type="TimelineEvent",
        entity_id=str(event.id),
    )
    db.commit()
    db.refresh(event)
    return event


@router.patch("/timeline/{event_id}", response_model=TimelineEventRead)
def update_timeline(
    event_id: int,
    payload: TimelineEventUpdate,
    actor: User = Depends(require_analyst),
    db: Session = Depends(get_db),
) -> TimelineEvent:
    event = db.get(TimelineEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Timeline event not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(event, field, value)
    audit_log(
        db,
        actor,
        "timeline.updated",
        case_id=event.case_id,
        entity_type="TimelineEvent",
        entity_id=str(event.id),
    )
    db.commit()
    db.refresh(event)
    return event


@router.delete("/timeline/{event_id}")
def delete_timeline(
    event_id: int, actor: User = Depends(require_analyst), db: Session = Depends(get_db)
) -> dict[str, str]:
    event = db.get(TimelineEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Timeline event not found")
    case_id = event.case_id
    db.delete(event)
    audit_log(
        db,
        actor,
        "timeline.deleted",
        case_id=case_id,
        entity_type="TimelineEvent",
        entity_id=str(event_id),
    )
    db.commit()
    return {"message": "deleted"}


@router.get("/cases/{case_id}/timeline/export.md")
def export_timeline(
    case_id: int, _: User = Depends(require_viewer), db: Session = Depends(get_db)
) -> Response:
    events = db.scalars(
        select(TimelineEvent)
        .where(TimelineEvent.case_id == case_id)
        .order_by(TimelineEvent.timestamp)
    ).all()
    markdown = "\n".join(
        (
            f"- {event.timestamp.isoformat()} [{event.event_type}] "
            f"{event.short_title}: {event.description}"
        )
        for event in events
    )
    return Response(markdown, media_type="text/markdown")
