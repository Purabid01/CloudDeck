import uuid
import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Column, String, Boolean, Text, 
    DateTime, Integer, Numeric, 
    ForeignKey, Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.session import Base


# Enums
class MemberRole(str, enum.Enum):
    requester = "requester"
    approver  = "approver"
    admin     = "admin"


class TaskStatus(str, enum.Enum):
    pending           = "pending"
    processing        = "processing"
    awaiting_approval = "awaiting_approval"
    approved          = "approved"
    rejected          = "rejected"
    provisioned       = "provisioned"
    failed            = "failed"


class SizingTier(str, enum.Enum):
    xs = "xs"
    s  = "s"
    m  = "m"
    l  = "l"


class BuildStatus(str, enum.Enum):
    pending  = "pending"
    running  = "running"
    complete = "complete"
    failed   = "failed"


class StageStatus(str, enum.Enum):
    provisioning = "provisioning"
    active       = "active"
    paused       = "paused"
    failed       = "failed"
    archived     = "archived"


class ReviewStatus(str, enum.Enum):
    pending_review = "pending_review"
    approved       = "approved"
    rejected       = "rejected"
    
    
#mixin
class TimestampMixin:
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    

# Models
class Member(TimestampMixin, Base):
    __tablename__ = "members"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    full_name = Column(
        String(255),
        nullable=False
    )
    hashed_password = Column(
        String,
        nullable=False
    )
    role = Column(
        SQLEnum(MemberRole),
        default=MemberRole.requester,
        nullable=False
    )
    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )
    
    tasks   = relationship("Task", back_populates="member")
    stages  = relationship("Stage", back_populates="member")
    reviews = relationship("Review", back_populates="approver")

    def __repr__(self):
        return f"<Member {self.email} [{self.role}]>"
    
    
class Template(TimestampMixin, Base):
    __tablename__ = "templates"

    id             = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name           = Column(String(255), nullable=False)
    slug           = Column(String(100), unique=True, nullable=False, index=True)  # URL-safe name e.g. "azure-web-portal"
    description    = Column(Text, nullable=False)       # used for vector embedding in RAG
    services       = Column(JSONB, nullable=False)      # [{"name": "App Service", "sku": "S1"}]
    base_cost_usd  = Column(Numeric(10, 2), nullable=False)
    cloud_provider = Column(String(50), nullable=False, default="azure")
    is_active      = Column(Boolean, default=True, nullable=False)

    tasks = relationship("Task", back_populates="template")

    def __repr__(self):
        return f"<Template {self.name} [{self.cloud_provider}]>"


class Task(TimestampMixin, Base):
    __tablename__ = "tasks"

    id                 = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    member_id          = Column(UUID(as_uuid=True), ForeignKey("members.id"), nullable=False, index=True)
    template_id        = Column(UUID(as_uuid=True), ForeignKey("templates.id"), nullable=True)   # set after pipeline runs
    name               = Column(String(255), nullable=False)
    description        = Column(Text, nullable=False)        # raw user input
    status             = Column(SQLEnum(TaskStatus), default=TaskStatus.pending, nullable=False, index=True)
    sizing_tier        = Column(SQLEnum(SizingTier), nullable=True)
    estimated_cost_usd = Column(Numeric(10, 2), nullable=True)
    generated_code     = Column(Text, nullable=True)         # IaC output from code generator agent
    metadata_          = Column("metadata", JSONB, default=dict)

    member   = relationship("Member", back_populates="tasks")
    template = relationship("Template", back_populates="tasks")
    builds   = relationship("Build", back_populates="task", order_by="Build.created_at")
    stage    = relationship("Stage", back_populates="task", uselist=False)   # one-to-one
    review   = relationship("Review", back_populates="task", uselist=False)  # one-to-one

    def __repr__(self):
        return f"<Task {self.name} [{self.status}]>"


class Build(TimestampMixin, Base):
    __tablename__ = "builds"

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id       = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False, index=True)
    agent_name    = Column(String(100), nullable=False)   # "intake", "classifier" etc
    status        = Column(SQLEnum(BuildStatus), default=BuildStatus.pending, nullable=False)
    input_data    = Column(JSONB, nullable=True)          # what the agent received
    output_data   = Column(JSONB, nullable=True)          # what the agent returned
    llm_prompt    = Column(Text, nullable=True)           # exact prompt sent to LLM
    llm_response  = Column(Text, nullable=True)           # raw LLM response before parsing
    duration_ms   = Column(Integer, nullable=True)        # how long agent took in milliseconds
    error_message = Column(Text, nullable=True)           # if failed, why

    task = relationship("Task", back_populates="builds")

    def __repr__(self):
        return f"<Build {self.agent_name} [{self.status}]>"


class Stage(TimestampMixin, Base):
    __tablename__ = "stages"

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id         = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), unique=True, nullable=False)  # one-to-one
    member_id       = Column(UUID(as_uuid=True), ForeignKey("members.id"), nullable=False, index=True)
    name            = Column(String(255), nullable=False)
    status          = Column(SQLEnum(StageStatus), default=StageStatus.provisioning, nullable=False, index=True)
    namespace       = Column(String(255), nullable=True)    # k8s namespace where it's deployed
    ttl_hours       = Column(Integer, default=4)            # auto-pause after 4 hours idle
    expires_at      = Column(DateTime(timezone=True), nullable=True)
    actual_cost_usd = Column(Numeric(10, 4), default=0)
    resources       = Column(JSONB, default=list)           # deployed k8s resources list

    task   = relationship("Task", back_populates="stage")
    member = relationship("Member", back_populates="stages")

    def __repr__(self):
        return f"<Stage {self.name} [{self.status}]>"


class Review(TimestampMixin, Base):
    __tablename__ = "reviews"

    id               = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id          = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), unique=True, nullable=False)  # one-to-one
    approver_id      = Column(UUID(as_uuid=True), ForeignKey("members.id"), nullable=True)   # null until reviewed
    status           = Column(SQLEnum(ReviewStatus), default=ReviewStatus.pending_review, nullable=False)
    rejection_reason = Column(Text, nullable=True)          # required when rejected
    reviewed_at      = Column(DateTime(timezone=True), nullable=True)  # when decision was made

    task     = relationship("Task", back_populates="review")
    approver = relationship("Member", back_populates="reviews")

    def __repr__(self):
        return f"<Review [{self.status}] for task {self.task_id}>"



