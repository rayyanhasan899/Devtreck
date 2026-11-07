"""add database-backed sensitive endpoint throttling"""

import sqlalchemy as sa
from alembic import op

revision = "73e8369b569c"
down_revision = "496d77b4d913"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_check_constraint(
        op.f("ck_users_theme_valid"), "users", "theme IN ('light', 'dark', 'system')"
    )
    op.create_check_constraint(op.f("ck_users_name_required"), "users", "length(btrim(name)) > 0")
    op.create_table(
        "rate_limits",
        sa.Column("key", sa.String(length=64), nullable=False),
        sa.Column("window", sa.Integer(), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("key", name=op.f("pk_rate_limits")),
    )

    op.create_index("ix_rate_limits_window", "rate_limits", ["window"])


def downgrade() -> None:
    op.drop_constraint(op.f("ck_users_theme_valid"), "users", type_="check")
    op.drop_constraint(op.f("ck_users_name_required"), "users", type_="check")
    op.drop_index("ix_rate_limits_window", table_name="rate_limits")
    op.drop_table("rate_limits")
