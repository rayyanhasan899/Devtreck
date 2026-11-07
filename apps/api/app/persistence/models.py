from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Float,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class UserModel(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "email = lower(btrim(email)) AND length(email) > 0", name="email_normalized"
        ),
        CheckConstraint("theme IN ('light', 'dark', 'system')", name="theme_valid"),
        CheckConstraint("length(btrim(name)) > 0", name="name_required"),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True)
    name: Mapped[str] = mapped_column(String(120))
    password_hash: Mapped[str] = mapped_column(String(512))
    time_zone: Mapped[str] = mapped_column(String(100), server_default="UTC")
    theme: Mapped[str] = mapped_column(String(10), server_default="system")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class SessionModel(Base):
    __tablename__ = "sessions"
    __table_args__ = (CheckConstraint("expires_at > created_at", name="positive_lifetime"),)
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class RateLimitModel(Base):
    __tablename__ = "rate_limits"
    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    window: Mapped[int] = mapped_column(Integer, index=True)
    attempts: Mapped[int] = mapped_column(Integer)


class CategoryModel(Base):
    __tablename__ = "categories"
    __table_args__ = (
        UniqueConstraint("id", "user_id"),
        UniqueConstraint("user_id", "name"),
        CheckConstraint("length(btrim(name)) > 0", name="name_required"),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(80))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class TaskModel(Base):
    __tablename__ = "tasks"
    __table_args__ = (
        UniqueConstraint("id", "user_id"),
        ForeignKeyConstraint(
            ["category_id", "user_id"],
            ["categories.id", "categories.user_id"],
            name="fk_tasks_category_owner",
            deferrable=True,
            initially="DEFERRED",
        ),
        CheckConstraint("length(btrim(title)) > 0", name="title_required"),
        CheckConstraint("status IN ('pending','in-progress','completed')", name="status_valid"),
        CheckConstraint("task_type IN ('one-time','daily')", name="type_valid"),
        CheckConstraint("priority IN ('low','medium','high')", name="priority_valid"),
        CheckConstraint(
            "estimated_minutes IS NULL OR estimated_minutes > 0", name="estimate_positive"
        ),
        CheckConstraint("due_date IS NULL OR due_at IS NULL", name="due_exclusive"),
        Index("ix_tasks_owner_status", "user_id", "status"),
        Index("ix_tasks_owner_due_date", "user_id", "due_date"),
        Index("ix_tasks_owner_due_at", "user_id", "due_at"),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    category_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL")
    )
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(String(10000))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    task_type: Mapped[str] = mapped_column(String(10), default="one-time")
    priority: Mapped[str] = mapped_column(String(10), default="medium")
    due_date: Mapped[date | None] = mapped_column(Date)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    estimated_minutes: Mapped[int | None] = mapped_column(Integer)
    daily_epoch: Mapped[UUID | None] = mapped_column()
    current_streak: Mapped[int] = mapped_column(Integer, server_default="0")
    best_streak: Mapped[int] = mapped_column(Integer, server_default="0")
    last_qualified_day: Mapped[date | None] = mapped_column(Date)
    daily_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class CompletionModel(Base):
    __tablename__ = "completions"
    __table_args__ = (
        ForeignKeyConstraint(
            ["task_id", "user_id"], ["tasks.id", "tasks.user_id"], ondelete="CASCADE"
        ),
        UniqueConstraint("task_id", name="uq_completions_one_time_task"),
        Index("ix_completions_owner_time", "user_id", "completed_at"),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    task_id: Mapped[UUID] = mapped_column()
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class TaskTypeChangeModel(Base):
    __tablename__ = "task_type_changes"
    __table_args__ = (
        ForeignKeyConstraint(
            ["task_id", "user_id"], ["tasks.id", "tasks.user_id"], ondelete="CASCADE"
        ),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    task_id: Mapped[UUID] = mapped_column()
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    previous_type: Mapped[str] = mapped_column(String(10))
    next_type: Mapped[str] = mapped_column(String(10))
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DailyCompletionModel(Base):
    __tablename__ = "daily_completions"
    __table_args__ = (
        ForeignKeyConstraint(
            ["task_id", "user_id"], ["tasks.id", "tasks.user_id"], ondelete="CASCADE"
        ),
        UniqueConstraint("task_id", "completion_day", name="uq_daily_task_day"),
        Index("ix_daily_owner_time", "user_id", "completed_at"),
        Index("ix_daily_task_epoch_day", "task_id", "epoch", "completion_day"),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    task_id: Mapped[UUID] = mapped_column()
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    epoch: Mapped[UUID] = mapped_column()
    completion_day: Mapped[date] = mapped_column(Date)
    time_zone: Mapped[str] = mapped_column(String(100))
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class DailyPlanModel(Base):
    __tablename__ = "daily_plans"
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    day: Mapped[date] = mapped_column(Date, primary_key=True)
    order_ids: Mapped[list[str]] = mapped_column(JSONB, default=list)
    priority_ids: Mapped[list[str]] = mapped_column(JSONB, default=list)


class ChecklistModel(Base):
    __tablename__ = "checklist_items"
    __table_args__ = (
        ForeignKeyConstraint(
            ["task_id", "user_id"], ["tasks.id", "tasks.user_id"], ondelete="CASCADE"
        ),
        UniqueConstraint(
            "task_id",
            "position",
            name="uq_checklist_position",
            deferrable=True,
            initially="DEFERRED",
        ),
        CheckConstraint("position >= 0", name="position_nonnegative"),
        CheckConstraint("length(btrim(title)) > 0", name="title_required"),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    task_id: Mapped[UUID] = mapped_column()
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(200))
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    position: Mapped[int] = mapped_column(Integer)


class FocusSessionModel(Base):
    __tablename__ = "focus_sessions"
    __table_args__ = (
        UniqueConstraint("id", "user_id"),
        ForeignKeyConstraint(
            ["task_id", "user_id"],
            ["tasks.id", "tasks.user_id"],
            name="fk_focus_task_owner",
            deferrable=True,
            initially="DEFERRED",
        ),
        Index(
            "uq_focus_running_user",
            "user_id",
            unique=True,
            postgresql_where=text("status IN ('active','paused')"),
        ),
        Index("ix_focus_owner_started", "user_id", "started_at"),
        CheckConstraint("status IN ('active','paused','completed','stopped')", name="status_valid"),
        CheckConstraint("kind IN ('focus','break')", name="kind_valid"),
        CheckConstraint(
            "target_seconds BETWEEN 60 AND 10800 AND elapsed_seconds >= 0 AND elapsed_seconds <= target_seconds",
            name="duration_valid",
        ),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    task_id: Mapped[UUID | None] = mapped_column(ForeignKey("tasks.id", ondelete="SET NULL"))
    kind: Mapped[str] = mapped_column(String(10))
    status: Mapped[str] = mapped_column(String(12), default="active")
    target_seconds: Mapped[int] = mapped_column(Integer)
    elapsed_seconds: Mapped[float] = mapped_column(Float, default=0)
    active_since: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class FocusEventModel(Base):
    __tablename__ = "focus_events"
    __table_args__ = (
        ForeignKeyConstraint(
            ["session_id", "user_id"],
            ["focus_sessions.id", "focus_sessions.user_id"],
            ondelete="CASCADE",
        ),
        UniqueConstraint("user_id", "command_key"),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    session_id: Mapped[UUID] = mapped_column()
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    command_key: Mapped[UUID] = mapped_column()
    action: Mapped[str] = mapped_column(String(10))
    fingerprint: Mapped[str] = mapped_column(String(64))
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class FocusIntervalModel(Base):
    __tablename__ = "focus_intervals"
    __table_args__ = (
        ForeignKeyConstraint(
            ["session_id", "user_id"],
            ["focus_sessions.id", "focus_sessions.user_id"],
            ondelete="CASCADE",
        ),
        CheckConstraint("ended_at >= started_at", name="interval_valid"),
        Index("ix_focus_intervals_owner_start", "user_id", "started_at"),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    session_id: Mapped[UUID] = mapped_column()
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class XPLedgerModel(Base):
    __tablename__ = "xp_ledger"
    __table_args__ = (
        UniqueConstraint("user_id", "source_kind", "source_id"),
        CheckConstraint("amount >= 0", name="amount_nonnegative"),
        Index("ix_xp_owner_day", "user_id", "reward_day"),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    source_kind: Mapped[str] = mapped_column(String(12))
    source_id: Mapped[UUID] = mapped_column()
    amount: Mapped[int] = mapped_column(Integer)
    reward_day: Mapped[date] = mapped_column(Date)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    awarded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    policy: Mapped[str] = mapped_column(String(200))


class AchievementModel(Base):
    __tablename__ = "achievements"
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    key: Mapped[str] = mapped_column(String(30), primary_key=True)
    earned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class OccurrenceModel(Base):
    __tablename__ = "eligible_occurrences"
    __table_args__ = (
        ForeignKeyConstraint(
            ["task_id", "user_id"], ["tasks.id", "tasks.user_id"], ondelete="CASCADE"
        ),
        UniqueConstraint("task_id", "kind", "day"),
        Index(
            "uq_occurrence_one_time",
            "task_id",
            unique=True,
            postgresql_where=text("kind = 'one_time'"),
        ),
        Index("ix_occurrences_owner_day", "user_id", "day"),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    task_id: Mapped[UUID] = mapped_column()
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    kind: Mapped[str] = mapped_column(String(12))
    day: Mapped[date] = mapped_column(Date)


class InsightDayModel(Base):
    __tablename__ = "insight_days"
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    day: Mapped[date] = mapped_column(Date, primary_key=True)
    time_zone: Mapped[str] = mapped_column(String(100))
