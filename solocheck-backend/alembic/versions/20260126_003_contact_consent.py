"""Add consent columns to emergency_contacts table.

Revision ID: 004
Revises: 003
Create Date: 2026-01-26

This migration adds consent-related columns to the emergency_contacts table
for the trust contact consent system.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add consent columns to emergency_contacts table."""
    # Add status column (pending, approved, rejected, expired)
    op.add_column(
        "emergency_contacts",
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default="pending",
            comment="Consent status: 'pending', 'approved', 'rejected', 'expired'",
        ),
    )

    # Add consent_requested_at column
    op.add_column(
        "emergency_contacts",
        sa.Column(
            "consent_requested_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="Timestamp when consent was requested",
        ),
    )

    # Add consent_responded_at column
    op.add_column(
        "emergency_contacts",
        sa.Column(
            "consent_responded_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="Timestamp when contact responded to consent request",
        ),
    )

    # Add consent_token column (unique, for consent URL)
    op.add_column(
        "emergency_contacts",
        sa.Column(
            "consent_token",
            sa.String(64),
            nullable=True,
            unique=True,
            comment="One-time token for consent URL",
        ),
    )

    # Add consent_expires_at column
    op.add_column(
        "emergency_contacts",
        sa.Column(
            "consent_expires_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="Expiration time for consent token (7 days)",
        ),
    )

    # Create index on consent_token for faster lookups
    op.create_index(
        "ix_emergency_contacts_consent_token",
        "emergency_contacts",
        ["consent_token"],
        unique=True,
    )


def downgrade() -> None:
    """Remove consent columns from emergency_contacts table."""
    op.drop_index("ix_emergency_contacts_consent_token", table_name="emergency_contacts")
    op.drop_column("emergency_contacts", "consent_expires_at")
    op.drop_column("emergency_contacts", "consent_token")
    op.drop_column("emergency_contacts", "consent_responded_at")
    op.drop_column("emergency_contacts", "consent_requested_at")
    op.drop_column("emergency_contacts", "status")
