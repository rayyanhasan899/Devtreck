"""add daily plans focus events intervals and checklists"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "e5fe82dd46cc"
down_revision = "686071c1a9b8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "daily_plans",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("day", sa.Date(), nullable=False),
        sa.Column("order_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("priority_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_daily_plans_user_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("user_id", "day", name=op.f("pk_daily_plans")),
    )
    op.create_table(
        "checklist_items",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("task_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("completed", sa.Boolean(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "length(btrim(title)) > 0", name=op.f("ck_checklist_items_title_required")
        ),
        sa.CheckConstraint("position >= 0", name=op.f("ck_checklist_items_position_nonnegative")),
        sa.ForeignKeyConstraint(
            ["task_id", "user_id"],
            ["tasks.id", "tasks.user_id"],
            name=op.f("fk_checklist_items_task_id_tasks"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_checklist_items_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_checklist_items")),
        sa.UniqueConstraint(
            "task_id",
            "position",
            deferrable=True,
            initially="DEFERRED",
            name="uq_checklist_position",
        ),
    )
    op.create_table(
        "focus_sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("task_id", sa.Uuid(), nullable=True),
        sa.Column("kind", sa.String(length=10), nullable=False),
        sa.Column("status", sa.String(length=12), nullable=False),
        sa.Column("target_seconds", sa.Integer(), nullable=False),
        sa.Column("elapsed_seconds", sa.Float(), nullable=False),
        sa.Column("active_since", sa.DateTime(timezone=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("kind IN ('focus','break')", name=op.f("ck_focus_sessions_kind_valid")),
        sa.CheckConstraint(
            "status IN ('active','paused','completed','stopped')",
            name=op.f("ck_focus_sessions_status_valid"),
        ),
        sa.CheckConstraint(
            "target_seconds BETWEEN 60 AND 10800 AND elapsed_seconds >= 0 AND elapsed_seconds <= target_seconds",
            name=op.f("ck_focus_sessions_duration_valid"),
        ),
        sa.ForeignKeyConstraint(
            ["task_id", "user_id"],
            ["tasks.id", "tasks.user_id"],
            name="fk_focus_task_owner",
            initially="DEFERRED",
            deferrable=True,
        ),
        sa.ForeignKeyConstraint(
            ["task_id"],
            ["tasks.id"],
            name=op.f("fk_focus_sessions_task_id_tasks"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_focus_sessions_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_focus_sessions")),
        sa.UniqueConstraint("id", "user_id", name=op.f("uq_focus_sessions_id")),
    )
    op.create_index(
        "ix_focus_owner_started", "focus_sessions", ["user_id", "started_at"], unique=False
    )
    op.create_index(
        "uq_focus_running_user",
        "focus_sessions",
        ["user_id"],
        unique=True,
        postgresql_where=sa.text("status IN ('active','paused')"),
    )
    op.create_table(
        "focus_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("command_key", sa.Uuid(), nullable=False),
        sa.Column("action", sa.String(length=10), nullable=False),
        sa.Column("fingerprint", sa.String(length=64), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["session_id", "user_id"],
            ["focus_sessions.id", "focus_sessions.user_id"],
            name=op.f("fk_focus_events_session_id_focus_sessions"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_focus_events_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_focus_events")),
        sa.UniqueConstraint("user_id", "command_key", name=op.f("uq_focus_events_user_id")),
    )
    op.create_table(
        "focus_intervals",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "ended_at >= started_at", name=op.f("ck_focus_intervals_interval_valid")
        ),
        sa.ForeignKeyConstraint(
            ["session_id", "user_id"],
            ["focus_sessions.id", "focus_sessions.user_id"],
            name=op.f("fk_focus_intervals_session_id_focus_sessions"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_focus_intervals_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_focus_intervals")),
    )
    op.create_index(
        "ix_focus_intervals_owner_start", "focus_intervals", ["user_id", "started_at"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_focus_intervals_owner_start", table_name="focus_intervals")
    op.drop_table("focus_intervals")
    op.drop_table("focus_events")
    op.drop_index(
        "uq_focus_running_user",
        table_name="focus_sessions",
        postgresql_where=sa.text("status IN ('active','paused')"),
    )
    op.drop_index("ix_focus_owner_started", table_name="focus_sessions")
    op.drop_table("focus_sessions")
    op.drop_table("checklist_items")
    op.drop_table("daily_plans")
