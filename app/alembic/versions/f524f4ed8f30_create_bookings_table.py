"""create_bookings_table

Revision ID: f524f4ed8f30
Revises: 87a5791a214c
Create Date: 2024-01-16 12:38:48.699281

"""
from alembic import op
from sqlalchemy.sql import text
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f524f4ed8f30'
down_revision = '87a5791a214c'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'bookings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('activity_id', sa.Integer(), nullable=False),
        sa.Column('time_slot_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['activity_id'], ['activities.id']),
        sa.ForeignKeyConstraint(['time_slot_id'], ['time_slots.id']),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('bookings')