"""create_user_table

Revision ID: ef14de4300b2
Revises: 3fa7ca3a955a
Create Date: 2024-01-16 11:42:38.111200

"""
from alembic import op
from sqlalchemy.sql import text
import sqlalchemy as sa



# revision identifiers, used by Alembic.
revision = 'ef14de4300b2'
down_revision = '3fa7ca3a955a'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False, unique=True),
        sa.Column('password', sa.String(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=text('now()')),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('users')
