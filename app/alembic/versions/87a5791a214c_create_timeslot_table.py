"""create_timeslot_table

Revision ID: 87a5791a214c
Revises: 06aa61255671
Create Date: 2024-01-16 12:35:06.790719

"""
from alembic import op
from sqlalchemy.sql import text
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '87a5791a214c'
down_revision = '06aa61255671'
branch_labels = None
depends_on = None



def upgrade():
    op.create_table(
        'time_slots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('start_time', sa.Time(), nullable=False),
        sa.Column('end_time', sa.Time(), nullable=False),
        sa.Column('max_capacity', sa.Integer(), nullable=False),
        sa.Column('is_available', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('activity_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=text('now()')),
        sa.ForeignKeyConstraint(['activity_id'], ['activities.id']),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('time_slots')