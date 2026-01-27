"""Add location consent and location sharing logs

Revision ID: 20260126_007
Revises: 20260126_006
Create Date: 2026-01-26
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY

revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add location consent columns to users table
    op.add_column(
        'users',
        sa.Column('location_consent', sa.Boolean, server_default='false', nullable=False)
    )
    op.add_column(
        'users',
        sa.Column('location_consent_at', sa.DateTime(timezone=True), nullable=True)
    )

    # Create location_sharing_logs table
    op.create_table(
        'location_sharing_logs',
        sa.Column('id', sa.String(36), primary_key=True, server_default=sa.text("gen_random_uuid()::text")),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False, comment='sos or missed_checkin'),
        sa.Column('location_lat', sa.Numeric(10, 8), nullable=True),
        sa.Column('location_lng', sa.Numeric(11, 8), nullable=True),
        sa.Column('recipient_ids', ARRAY(sa.String(36)), nullable=True),
        sa.Column('shared_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    op.create_index('ix_location_sharing_logs_user_id', 'location_sharing_logs', ['user_id'])
    op.create_index('ix_location_sharing_logs_event_type', 'location_sharing_logs', ['event_type'])
    op.create_index('ix_location_sharing_logs_shared_at', 'location_sharing_logs', ['shared_at'])


def downgrade() -> None:
    op.drop_index('ix_location_sharing_logs_shared_at')
    op.drop_index('ix_location_sharing_logs_event_type')
    op.drop_index('ix_location_sharing_logs_user_id')
    op.drop_table('location_sharing_logs')

    op.drop_column('users', 'location_consent_at')
    op.drop_column('users', 'location_consent')
