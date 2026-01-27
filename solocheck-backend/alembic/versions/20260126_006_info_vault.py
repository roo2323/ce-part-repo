"""Create info_vault table

Revision ID: 20260126_006
Revises: 20260126_005
Create Date: 2026-01-26
"""
from alembic import op
import sqlalchemy as sa

revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'info_vault',
        sa.Column('id', sa.String(36), primary_key=True, server_default=sa.text("gen_random_uuid()::text")),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('content_encrypted', sa.Text, nullable=False),
        sa.Column('include_in_alert', sa.Boolean, server_default='false', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    op.create_index('ix_info_vault_user_id', 'info_vault', ['user_id'])
    op.create_index('ix_info_vault_category', 'info_vault', ['category'])


def downgrade() -> None:
    op.drop_index('ix_info_vault_category')
    op.drop_index('ix_info_vault_user_id')
    op.drop_table('info_vault')
