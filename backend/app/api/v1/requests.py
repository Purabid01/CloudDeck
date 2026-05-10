from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from uuid import UUID
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_active_member, require_approver
from app.db import crud
from app.db.models import Member
from app.db.schemas import TaskCreate, TaskResponse, ReviewDecision
from app.agents.pipeline import run_pipeline

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(
    data: TaskCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_member: Member = Depends(get_current_active_member)
):
    task = crud.create_task(db, data, current_member.id)
    # run pipeline in background — don't make client wait
    background_tasks.add_task(run_pipeline, task.id, db)
    return task


@router.get("/", response_model=list[TaskResponse])
def get_my_tasks(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_member: Member = Depends(get_current_active_member)
):
    return crud.get_tasks_for_member(db, current_member.id, skip, limit)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_member: Member = Depends(get_current_active_member)
):
    task = crud.get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.member_id != current_member.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return task