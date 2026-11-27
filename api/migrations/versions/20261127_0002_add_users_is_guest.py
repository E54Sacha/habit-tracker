"""Add users.is_guest for "Try as guest" accounts

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-27
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # server_default fills the existing rows with false, so NOT NULL works on a table with data.
    op.add_column("users", sa.Column("is_guest", sa.Boolean(), server_default=sa.false(), nullable=False))
    # Finding old guests to delete must stay fast as the table grows.
    op.create_index("ix_users_guest_created_at", "users", ["created_at"], postgresql_where=sa.text("is_guest"))


def downgrade() -> None:
    op.drop_index("ix_users_guest_created_at", table_name="users")
    op.drop_column("users", "is_guest")
