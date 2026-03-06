"""add user auth fields

Revision ID: 20260306_0002
Revises: 20260306_0001
Create Date: 2026-03-06 14:50:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260306_0002"
down_revision = "20260306_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("password_hash", sa.String(length=255), nullable=True))
    op.add_column("users", sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("users", sa.Column("password_updated_at", sa.DateTime(timezone=True), nullable=True))

    op.execute("UPDATE users SET password_hash = '' WHERE password_hash IS NULL")
    op.alter_column("users", "password_hash", nullable=False)


def downgrade() -> None:
    op.drop_column("users", "password_updated_at")
    op.drop_column("users", "last_login_at")
    op.drop_column("users", "password_hash")
