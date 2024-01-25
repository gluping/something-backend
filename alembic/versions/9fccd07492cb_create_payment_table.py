"""create_payment_table

Revision ID: 9fccd07492cb
Revises: f524f4ed8f30
Create Date: 2024-01-16 12:40:09.756234

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9fccd07492cb'
down_revision = 'f524f4ed8f30'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'payments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='Pending'),
        sa.Column('booking_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['booking_id'], ['bookings.id']),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('payments')
