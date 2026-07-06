from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_analyst, require_viewer
from app.db.session import get_db
from app.models import Task, User
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate
from app.services.audit import audit_log

router = APIRouter(tags=["tasks"])


@router.get("/cases/{case_id}/tasks", response_model=list[TaskRead])
def list_tasks(case_id: int, _: User = Depends(require_viewer), db: Session = Depends(get_db)):
    return list(db.scalars(select(Task).where(Task.case_id == case_id).order_by(Task.id)).all())


@router.post("/cases/{case_id}/tasks", response_model=TaskRead)
def create_task(
    case_id: int,
    payload: TaskCreate,
    actor: User = Depends(require_analyst),
    db: Session = Depends(get_db),
) -> Task:
    task = Task(case_id=case_id, **payload.model_dump())
    db.add(task)
    db.flush()
    audit_log(
        db, actor, "task.created", case_id=case_id, entity_type="Task", entity_id=str(task.id)
    )
    db.commit()
    db.refresh(task)
    return task


@router.patch("/tasks/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    actor: User = Depends(require_analyst),
    db: Session = Depends(get_db),
) -> Task:
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    old_status = task.status
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    if payload.status and payload.status != old_status:
        audit_log(
            db,
            actor,
            "task.completed" if payload.status.value == "Done" else "task.status_changed",
            case_id=task.case_id,
            entity_type="Task",
            entity_id=str(task.id),
        )
    else:
        audit_log(
            db,
            actor,
            "task.updated",
            case_id=task.case_id,
            entity_type="Task",
            entity_id=str(task.id),
        )
    db.commit()
    db.refresh(task)
    return task
