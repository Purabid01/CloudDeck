from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models import (
    Member, Template, Task, Build,
    Stage, Review, TaskStatus, BuildStatus,
    StageStatus, ReviewStatus, MemberRole
)
from app.db.schemas import (
    MemberCreate, TaskCreate, ReviewDecision
)
from app.core.security import hash_password


# ── Member CRUD ────────────────────────────────────────

def get_member_by_email(db: Session, email: str) -> Optional[Member]:
    return db.query(Member).filter(Member.email == email).first()


def get_member_by_id(db: Session, member_id: UUID) -> Optional[Member]:
    return db.query(Member).filter(Member.id == member_id).first()


def get_all_members(db: Session, skip: int = 0, limit: int = 20) -> list[Member]:
    return db.query(Member).offset(skip).limit(limit).all()


def create_member(db: Session, data: MemberCreate) -> Member:
    member = Member(
        email=data.email,
        full_name=data.full_name,
        hashed_password=hash_password(data.password),  # never store plain text
    )
    db.add(member)
    db.commit()
    db.refresh(member)   # refresh loads the generated id, created_at etc
    return member


def update_member_role(db: Session, member_id: UUID, role: MemberRole) -> Optional[Member]:
    member = get_member_by_id(db, member_id)
    if not member:
        return None
    member.role = role
    db.commit()
    db.refresh(member)
    return member


def deactivate_member(db: Session, member_id: UUID) -> Optional[Member]:
    member = get_member_by_id(db, member_id)
    if not member:
        return None
    member.is_active = False
    db.commit()
    db.refresh(member)
    return member


# ── Template CRUD ──────────────────────────────────────

def get_all_templates(db: Session, skip: int = 0, limit: int = 20) -> list[Template]:
    return db.query(Template).filter(Template.is_active == True).offset(skip).limit(limit).all()


def get_template_by_id(db: Session, template_id: UUID) -> Optional[Template]:
    return db.query(Template).filter(Template.id == template_id).first()


def get_template_by_slug(db: Session, slug: str) -> Optional[Template]:
    return db.query(Template).filter(Template.slug == slug).first()


# ── Task CRUD ──────────────────────────────────────────

def create_task(db: Session, data: TaskCreate, member_id: UUID) -> Task:
    task = Task(
        name=data.name,
        description=data.description,
        member_id=member_id,
        status=TaskStatus.pending
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_task_by_id(db: Session, task_id: UUID) -> Optional[Task]:
    return db.query(Task).filter(Task.id == task_id).first()


def get_tasks_for_member(db: Session, member_id: UUID, skip: int = 0, limit: int = 20) -> list[Task]:
    return (
        db.query(Task)
        .filter(Task.member_id == member_id)
        .order_by(Task.created_at.desc())   # newest first
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_all_tasks(db: Session, skip: int = 0, limit: int = 20) -> list[Task]:
    """Admin only — see all tasks"""
    return db.query(Task).order_by(Task.created_at.desc()).offset(skip).limit(limit).all()


def update_task_status(db: Session, task_id: UUID, status: TaskStatus) -> Optional[Task]:
    task = get_task_by_id(db, task_id)
    if not task:
        return None
    task.status = status
    db.commit()
    db.refresh(task)
    return task


def update_task_pipeline_result(
    db: Session,
    task_id: UUID,
    template_id: Optional[UUID] = None,
    sizing_tier=None,
    estimated_cost_usd: Optional[float] = None,
    generated_code: Optional[str] = None,
    status: Optional[TaskStatus] = None
) -> Optional[Task]:
    """Called by agent pipeline to update task as each agent completes"""
    task = get_task_by_id(db, task_id)
    if not task:
        return None
    if template_id:
        task.template_id = template_id
    if sizing_tier:
        task.sizing_tier = sizing_tier
    if estimated_cost_usd:
        task.estimated_cost_usd = estimated_cost_usd
    if generated_code:
        task.generated_code = generated_code
    if status:
        task.status = status
    db.commit()
    db.refresh(task)
    return task


# ── Build CRUD ─────────────────────────────────────────

def create_build(db: Session, task_id: UUID, agent_name: str) -> Build:
    """Create a build record when an agent starts"""
    build = Build(
        task_id=task_id,
        agent_name=agent_name,
        status=BuildStatus.pending
    )
    db.add(build)
    db.commit()
    db.refresh(build)
    return build


def update_build(
    db: Session,
    build_id: UUID,
    status: BuildStatus,
    input_data: Optional[dict] = None,
    output_data: Optional[dict] = None,
    llm_prompt: Optional[str] = None,
    llm_response: Optional[str] = None,
    duration_ms: Optional[int] = None,
    error_message: Optional[str] = None
) -> Optional[Build]:
    build = db.query(Build).filter(Build.id == build_id).first()
    if not build:
        return None
    build.status = status
    if input_data:
        build.input_data = input_data
    if output_data:
        build.output_data = output_data
    if llm_prompt:
        build.llm_prompt = llm_prompt
    if llm_response:
        build.llm_response = llm_response
    if duration_ms:
        build.duration_ms = duration_ms
    if error_message:
        build.error_message = error_message
    db.commit()
    db.refresh(build)
    return build


def get_builds_for_task(db: Session, task_id: UUID) -> list[Build]:
    return (
        db.query(Build)
        .filter(Build.task_id == task_id)
        .order_by(Build.created_at.asc())   # oldest first — shows pipeline order
        .all()
    )


# ── Review CRUD ────────────────────────────────────────

def create_review(db: Session, task_id: UUID) -> Review:
    """Created automatically when pipeline reaches awaiting_approval"""
    review = Review(
        task_id=task_id,
        status=ReviewStatus.pending_review
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def get_review_by_task(db: Session, task_id: UUID) -> Optional[Review]:
    return db.query(Review).filter(Review.task_id == task_id).first()


def get_pending_reviews(db: Session, skip: int = 0, limit: int = 20) -> list[Review]:
    """Approver dashboard — all tasks waiting for review"""
    return (
        db.query(Review)
        .filter(Review.status == ReviewStatus.pending_review)
        .order_by(Review.created_at.asc())   # oldest first — FIFO queue
        .offset(skip)
        .limit(limit)
        .all()
    )


def decide_review(
    db: Session,
    task_id: UUID,
    approver_id: UUID,
    decision: ReviewDecision
) -> Optional[Review]:
    review = get_review_by_task(db, task_id)
    if not review:
        return None
    review.approver_id = approver_id
    review.reviewed_at = datetime.now(timezone.utc)
    if decision.approved:
        review.status = ReviewStatus.approved
        update_task_status(db, task_id, TaskStatus.approved)
    else:
        review.status = ReviewStatus.rejected
        review.rejection_reason = decision.rejection_reason
        update_task_status(db, task_id, TaskStatus.rejected)
    db.commit()
    db.refresh(review)
    return review


# ── Stage CRUD ─────────────────────────────────────────

def create_stage(db: Session, task_id: UUID, member_id: UUID, name: str) -> Stage:
    stage = Stage(
        task_id=task_id,
        member_id=member_id,
        name=name,
        status=StageStatus.provisioning
    )
    db.add(stage)
    db.commit()
    db.refresh(stage)
    return stage


def get_stages_for_member(db: Session, member_id: UUID) -> list[Stage]:
    return (
        db.query(Stage)
        .filter(Stage.member_id == member_id)
        .order_by(Stage.created_at.desc())
        .all()
    )


def update_stage_status(db: Session, stage_id: UUID, status: StageStatus) -> Optional[Stage]:
    stage = db.query(Stage).filter(Stage.id == stage_id).first()
    if not stage:
        return None
    stage.status = status
    db.commit()
    db.refresh(stage)
    return stage