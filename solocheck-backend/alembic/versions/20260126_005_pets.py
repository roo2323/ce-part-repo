"""Create pets table

Revision ID: 20260126_005
Revises: 20260126_004
Create Date: 2026-01-26
"""
from alembic import op
import sqlalchemy as sa

revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'pets',
        sa.Column('id', sa.String(36), primary_key=True, server_default=sa.text("gen_random_uuid()::text")),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('species', sa.String(50), nullable=False),
        sa.Column('breed', sa.String(100), nullable=True),
        sa.Column('birth_date', sa.Date, nullable=True),
        sa.Column('weight', sa.Numeric(5, 2), nullable=True),
        sa.Column('medical_notes', sa.Text, nullable=True),
        sa.Column('vet_info', sa.Text, nullable=True),
        sa.Column('caretaker_contact', sa.String(200), nullable=True),
        sa.Column('photo_url', sa.String(500), nullable=True),
        sa.Column('include_in_alert', sa.Boolean, server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    op.create_index('ix_pets_user_id', 'pets', ['user_id'])


def downgrade() -> None:
    op.drop_index('ix_pets_user_id')
    op.drop_table('pets')
