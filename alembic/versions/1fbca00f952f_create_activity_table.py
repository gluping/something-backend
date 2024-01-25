"""create_activity_table

Revision ID: 1fbca00f952f
Revises: ef14de4300b2
Create Date: 2024-01-16 12:31:23.491528

"""
from alembic import op
from sqlalchemy.sql import text
import sqlalchemy as sa



# revision identifiers, used by Alembic.
revision = '1fbca00f952f'
down_revision = 'ef14de4300b2'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'activity_providers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('business_name', sa.String(), nullable=False),
        sa.Column('contact_email', sa.String(), nullable=False, unique=True),
        sa.Column('password', sa.String(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=text('now()')),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('activity_providers')