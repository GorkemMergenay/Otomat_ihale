"""notification_subscribers table

Revision ID: 20260306_0003
Revises: 20260306_0002
Create Date: 2026-03-06

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260306_0003"
down_revision = "20260306_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "notification_subscribers",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("label", sa.String(length=100), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_notification_subscribers_email", "notification_subscribers", ["email"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_notification_subscribers_email", table_name="notification_subscribers")
    op.drop_table("notification_subscribers")
