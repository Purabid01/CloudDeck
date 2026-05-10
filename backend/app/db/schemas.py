from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, field_validator

from app.db.models import (
    MemberRole, TaskStatus, SizingTier,
    BuildStatus, StageStatus, ReviewStatus
)


# ── Base schemas ───────────────────────────────────────
# These are reusable base classes — same pattern as TimestampMixin
# but for Pydantic schemas

class TimestampSchema(BaseModel):
    created_at: datetime
    updated_at: datetime


# ── Member schemas ─────────────────────────────────────

class MemberCreate(BaseModel):
    """What the client sends when registering"""
    email: str
    password: str          # plain text — we hash it in the service layer
    full_name: str

    @field_validator("email")
    @classmethod
    def email_must_be_lowercase(cls, v):
        return v.lower().strip()   # always store emails lowercase


class MemberLogin(BaseModel):
    """What the client sends when logging in"""
    email: str
    password: str


class MemberResponse(TimestampSchema):
    """What the API returns — never includes password"""
    id: UUID
    email: str
    full_name: str
    role: MemberRole
    is_active: bool

    model_config = {"from_attributes": True}  # allows converting SQLAlchemy object → Pydantic


class MemberUpdate(BaseModel):
    """What the client sends to update their profile"""
    full_name: Optional[str] = None
    email: Optional[str] = None


# ── Token schemas ──────────────────────────────────────

class Token(BaseModel):
    """What the API returns after successful login"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """What lives inside the JWT token"""
    sub: str        # subject — the member's UUID
    exp: datetime   # expiry time


# ── Template schemas ───────────────────────────────────

class TemplateResponse(TimestampSchema):
    id: UUID
    name: str
    slug: str
    description: str
    services: list
    base_cost_usd: float
    cloud_provider: str
    is_active: bool

    model_config = {"from_attributes": True}


# ── Task schemas ───────────────────────────────────────

class TaskCreate(BaseModel):
    """What the client sends when submitting a new task"""
    name: str
    description: str    # plain English — "I want a web portal for..."


class TaskResponse(TimestampSchema):
    id: UUID
    name: str
    description: str
    status: TaskStatus
    sizing_tier: Optional[SizingTier] = None
    estimated_cost_usd: Optional[float] = None
    member_id: UUID
    template_id: Optional[UUID] = None

    model_config = {"from_attributes": True}


class TaskDetailResponse(TaskResponse):
    """Full task with all related data — used for single task view"""
    builds: list = []
    stage: Optional[dict] = None
    review: Optional[dict] = None


# ── Build schemas ──────────────────────────────────────

class BuildResponse(TimestampSchema):
    id: UUID
    agent_name: str
    status: BuildStatus
    input_data: Optional[dict] = None
    output_data: Optional[dict] = None
    duration_ms: Optional[int] = None
    error_message: Optional[str] = None

    model_config = {"from_attributes": True}


# ── Stage schemas ──────────────────────────────────────

class StageResponse(TimestampSchema):
    id: UUID
    name: str
    status: StageStatus
    namespace: Optional[str] = None
    ttl_hours: int
    actual_cost_usd: float
    resources: list

    model_config = {"from_attributes": True}


# ── Review schemas ─────────────────────────────────────

class ReviewResponse(TimestampSchema):
    id: UUID
    task_id: UUID
    status: ReviewStatus
    rejection_reason: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    approver_id: Optional[UUID] = None

    model_config = {"from_attributes": True}


class ReviewDecision(BaseModel):
    """What approver sends when making a decision"""
    approved: bool
    rejection_reason: Optional[str] = None

    @field_validator("rejection_reason")
    @classmethod
    def reason_required_if_rejected(cls, v, info):
        if info.data.get("approved") is False and not v:
            raise ValueError("rejection_reason is required when rejecting")
        return v


# ── Generic response schemas ───────────────────────────

class MessageResponse(BaseModel):
    """Simple message response"""
    message: str


class PaginatedResponse(BaseModel):
    """Wrapper for paginated list responses"""
    items: list
    total: int
    page: int
    limit: int
    pages: int