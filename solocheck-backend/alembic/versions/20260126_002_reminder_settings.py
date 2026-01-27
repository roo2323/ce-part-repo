"""Add reminder_settings table for customizable check-in reminders.

Revision ID: 003
Revises: 002
Create Date: 2026-01-26

This migration creates the reminder_settings table for storing
user's customizable reminder preferences.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY


# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create reminder_settings table."""
    op.create_table(
        "reminder_settings",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            unique=True,
            nullable=False,
            index=True,
        ),
        sa.Column(
            "reminder_hours_before",
            ARRAY(sa.Integer),
            nullable=False,
            server_default="{48,24,12}",
            comment="Hours before deadline to send reminders (default [48, 24, 12])",
        ),
        sa.Column(
            "quiet_hours_start",
            sa.Time(),
            nullable=True,
            comment="Start of quiet hours (no notifications)",
        ),
        sa.Column(
            "quiet_hours_end",
            sa.Time(),
            nullable=True,
            comment="End of quiet hours",
        ),
        sa.Column(
            "preferred_time",
            sa.Time(),
            nullable=True,
            comment="Preferred time for receiving reminders",
        ),
        sa.Column(
            "push_enabled",
            sa.Boolean(),
            nullable=False,
            default=True,
            server_default="true",
            comment="Enable push notification reminders",
        ),
        sa.Column(
            "email_enabled",
            sa.Boolean(),
            nullable=False,
            default=False,
            server_default="false",
            comment="Enable email reminders",
        ),
        sa.Column(
            "custom_message",
            sa.String(100),
            nullable=True,
            comment="Custom reminder message (max 100 chars)",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )


def downgrade() -> None:
    """Drop reminder_settings table."""
    op.drop_table("reminder_settings")
