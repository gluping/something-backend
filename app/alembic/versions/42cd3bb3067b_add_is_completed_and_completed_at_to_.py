"""Add is_completed and completed_at to Booking

Revision ID: 42cd3bb3067b
Revises: 
Create Date: 2024-02-17 00:45:38.805369

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision: str = '42cd3bb3067b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add columns 'completed_at' and 'is_completed'
    op.add_column('bookings', sa.Column('completed_at', sa.TIMESTAMP(timezone=True), nullable=True))
    op.add_column('bookings', sa.Column('is_completed', sa.Boolean(), server_default='false'))

def downgrade() -> None:
    # Drop columns 'completed_at' and 'is_completed'
    op.drop_column('bookings', 'completed_at')
    op.drop_column('bookings', 'is_completed')
