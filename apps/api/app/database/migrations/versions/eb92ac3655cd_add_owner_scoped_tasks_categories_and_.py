"""add owner-scoped tasks categories and immutable completion facts"""

import sqlalchemy as sa
from alembic import op

revision = "eb92ac3655cd"
down_revision = "73e8369b569c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "categories",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("length(btrim(name)) > 0", name=op.f("ck_categories_name_required")),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_categories_user_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_categories")),
        sa.UniqueConstraint("id", "user_id", name=op.f("uq_categories_id")),
        sa.UniqueConstraint("user_id", "name", name=op.f("uq_categories_user_id")),
    )
    op.create_index(op.f("ix_categories_user_id"), "categories", ["user_id"], unique=False)
    op.create_table(
        "tasks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("category_id", sa.Uuid(), nullable=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.String(length=10000), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("task_type", sa.String(length=10), nullable=False),
        sa.Column("priority", sa.String(length=10), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("estimated_minutes", sa.Integer(), nullable=True),
        sa.Column("daily_started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "priority IN ('low','medium','high')", name=op.f("ck_tasks_priority_valid")
        ),
        sa.CheckConstraint(
            "status IN ('pending','in-progress','completed')", name=op.f("ck_tasks_status_valid")
        ),
        sa.CheckConstraint("task_type IN ('one-time','daily')", name=op.f("ck_tasks_type_valid")),
        sa.CheckConstraint(
            "due_date IS NULL OR due_at IS NULL", name=op.f("ck_tasks_due_exclusive")
        ),
        sa.CheckConstraint(
            "estimated_minutes IS NULL OR estimated_minutes > 0",
            name=op.f("ck_tasks_estimate_positive"),
        ),
        sa.CheckConstraint("length(btrim(title)) > 0", name=op.f("ck_tasks_title_required")),
        sa.ForeignKeyConstraint(
            ["category_id", "user_id"],
            ["categories.id", "categories.user_id"],
            name="fk_tasks_category_owner",
            deferrable=True,
            initially="DEFERRED",
        ),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["categories.id"],
            name=op.f("fk_tasks_category_id_categories"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_tasks_user_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tasks")),
        sa.UniqueConstraint("id", "user_id", name=op.f("uq_tasks_id")),
    )
    op.create_index("ix_tasks_owner_due_at", "tasks", ["user_id", "due_at"], unique=False)
    op.create_index("ix_tasks_owner_due_date", "tasks", ["user_id", "due_date"], unique=False)
    op.create_index("ix_tasks_owner_status", "tasks", ["user_id", "status"], unique=False)
    op.create_table(
        "completions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("task_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column(
            "completed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["task_id", "user_id"],
            ["tasks.id", "tasks.user_id"],
            name=op.f("fk_completions_task_id_tasks"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_completions_user_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_completions")),
        sa.UniqueConstraint("task_id", name="uq_completions_one_time_task"),
    )
    op.create_index(
        "ix_completions_owner_time", "completions", ["user_id", "completed_at"], unique=False
    )
    op.create_table(
        "task_type_changes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("task_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("previous_type", sa.String(length=10), nullable=False),
        sa.Column("next_type", sa.String(length=10), nullable=False),
        sa.Column(
            "changed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["task_id", "user_id"],
            ["tasks.id", "tasks.user_id"],
            name=op.f("fk_task_type_changes_task_id_tasks"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_task_type_changes_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_task_type_changes")),
    )


def downgrade() -> None:
    op.drop_table("task_type_changes")
    op.drop_index("ix_completions_owner_time", table_name="completions")
    op.drop_table("completions")
    op.drop_index("ix_tasks_owner_status", table_name="tasks")
    op.drop_index("ix_tasks_owner_due_date", table_name="tasks")
    op.drop_index("ix_tasks_owner_due_at", table_name="tasks")
    op.drop_table("tasks")
    op.drop_index(op.f("ix_categories_user_id"), table_name="categories")
    op.drop_table("categories")
