"""Add sos_events table for SOS emergency feature.

Revision ID: 005
Revises: 004
Create Date: 2026-01-26

This migration creates the sos_events table for tracking
SOS emergency triggers and notifications.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create sos_events table."""
    op.create_table(
        "sos_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "triggered_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
            comment="When the SOS was triggered",
        ),
        sa.Column(
            "cancelled_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="When the SOS was cancelled (if cancelled)",
        ),
        sa.Column(
            "sent_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="When notifications were sent",
        ),
        sa.Column(
            "location_lat",
            sa.Numeric(precision=10, scale=8),
            nullable=True,
            comment="Latitude at trigger time",
        ),
        sa.Column(
            "location_lng",
            sa.Numeric(precision=11, scale=8),
            nullable=True,
            comment="Longitude at trigger time",
        ),
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default="triggered",
            comment="SOS status: 'triggered', 'cancelled', 'sent'",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )


def downgrade() -> None:
    """Drop sos_events table."""
    op.drop_table("sos_events")
