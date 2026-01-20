"""Initial schema for SoloCheck database.

Revision ID: 001
Revises:
Create Date: 2025-01-19

This migration creates all initial tables:
- users: User accounts and check-in settings
- check_in_logs: Check-in history records
- emergency_contacts: Emergency contact information
- personal_messages: Personal messages for emergency contacts
- notification_logs: Notification delivery tracking
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema - create all tables."""
    # Create users table
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("nickname", sa.String(100), nullable=True),
        sa.Column(
            "check_in_cycle",
            sa.Integer(),
            nullable=False,
            default=7,
            comment="Check-in cycle in days (7, 14, or 30)",
        ),
        sa.Column(
            "grace_period",
            sa.Integer(),
            nullable=False,
            default=48,
            comment="Grace period in hours (24, 48, or 72)",
        ),
        sa.Column("last_check_in", sa.DateTime(timezone=True), nullable=True),
        sa.Column("fcm_token", sa.String(500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
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

    # Create check_in_logs table
    op.create_table(
        "check_in_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "checked_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "method",
            sa.String(50),
            nullable=True,
            comment="Check-in method: 'app_open', 'button_click', 'push_response'",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    # Create emergency_contacts table
    op.create_table(
        "emergency_contacts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column(
            "contact_type",
            sa.String(20),
            nullable=False,
            comment="Contact type: 'email' or 'sms'",
        ),
        sa.Column("contact_value", sa.String(255), nullable=False),
        sa.Column(
            "priority",
            sa.Integer(),
            nullable=False,
            default=1,
            comment="Contact priority (1 = highest)",
        ),
        sa.Column("is_verified", sa.Boolean(), nullable=False, default=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    # Create personal_messages table
    op.create_table(
        "personal_messages",
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
            "content",
            sa.Text(),
            nullable=False,
            comment="Encrypted personal message content (max 2000 characters)",
        ),
        sa.Column("is_enabled", sa.Boolean(), nullable=False, default=True),
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

    # Create notification_logs table
    op.create_table(
        "notification_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "contact_id",
            sa.String(36),
            sa.ForeignKey("emergency_contacts.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "type",
            sa.String(50),
            nullable=True,
            comment="Notification type: 'status_alert' or 'personal_message'",
        ),
        sa.Column(
            "status",
            sa.String(20),
            nullable=True,
            comment="Delivery status: 'pending', 'sent', or 'failed'",
        ),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.String(500), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )


def downgrade() -> None:
    """Downgrade database schema - drop all tables."""
    op.drop_table("notification_logs")
    op.drop_table("personal_messages")
    op.drop_table("emergency_contacts")
    op.drop_table("check_in_logs")
    op.drop_table("users")
