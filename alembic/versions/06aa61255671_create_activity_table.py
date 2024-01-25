"""create_activity_table

Revision ID: 06aa61255671
Revises: 1fbca00f952f
Create Date: 2024-01-16 12:33:20.835222

"""
from alembic import op
from sqlalchemy.sql import text
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '06aa61255671'
down_revision = '1fbca00f952f'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'activities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('location', sa.String(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('image_url', sa.String()),
        sa.Column('provider_id', sa.Integer(), nullable=False),
        sa.Column('likes', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=text('now()')),
        sa.ForeignKeyConstraint(['provider_id'], ['activity_providers.id']),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('activities')
