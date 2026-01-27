"""Add checkin_session_tokens table for quick check-in via push notification.

Revision ID: 002
Revises: 001
Create Date: 2026-01-26

This migration creates the checkin_session_tokens table for managing
one-time tokens that allow users to check-in directly from push notifications.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create checkin_session_tokens table."""
    op.create_table(
        "checkin_session_tokens",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "token",
            sa.String(64),
            unique=True,
            nullable=False,
            index=True,
            comment="One-time session token for push notification check-in",
        ),
        sa.Column(
            "expires_at",
            sa.DateTime(timezone=True),
            nullable=False,
            comment="Token expiration time (default 1 hour)",
        ),
        sa.Column(
            "used_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="Timestamp when token was used",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )


def downgrade() -> None:
    """Drop checkin_session_tokens table."""
    op.drop_table("checkin_session_tokens")
