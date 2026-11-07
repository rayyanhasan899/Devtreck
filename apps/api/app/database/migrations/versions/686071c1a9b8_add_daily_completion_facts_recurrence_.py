"""add daily completion facts recurrence epochs and streak caches"""

import sqlalchemy as sa
from alembic import op

revision = "686071c1a9b8"
down_revision = "eb92ac3655cd"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "daily_completions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("task_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("epoch", sa.Uuid(), nullable=False),
        sa.Column("completion_day", sa.Date(), nullable=False),
        sa.Column("time_zone", sa.String(length=100), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["task_id", "user_id"],
            ["tasks.id", "tasks.user_id"],
            name=op.f("fk_daily_completions_task_id_tasks"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_daily_completions_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_daily_completions")),
        sa.UniqueConstraint("task_id", "completion_day", name="uq_daily_task_day"),
    )
    op.create_index(
        "ix_daily_owner_time", "daily_completions", ["user_id", "completed_at"], unique=False
    )
    op.create_index(
        "ix_daily_task_epoch_day",
        "daily_completions",
        ["task_id", "epoch", "completion_day"],
        unique=False,
    )
    op.add_column("tasks", sa.Column("daily_epoch", sa.Uuid(), nullable=True))
    op.add_column(
        "tasks", sa.Column("current_streak", sa.Integer(), server_default="0", nullable=False)
    )
    op.add_column(
        "tasks", sa.Column("best_streak", sa.Integer(), server_default="0", nullable=False)
    )
    op.add_column("tasks", sa.Column("last_qualified_day", sa.Date(), nullable=True))

    op.execute(
        "UPDATE tasks SET daily_epoch = gen_random_uuid() WHERE task_type = 'daily' AND daily_epoch IS NULL"
    )


def downgrade() -> None:
    op.drop_column("tasks", "last_qualified_day")
    op.drop_column("tasks", "best_streak")
    op.drop_column("tasks", "current_streak")
    op.drop_column("tasks", "daily_epoch")
    op.drop_index("ix_daily_task_epoch_day", table_name="daily_completions")
    op.drop_index("ix_daily_owner_time", table_name="daily_completions")
    op.drop_table("daily_completions")
