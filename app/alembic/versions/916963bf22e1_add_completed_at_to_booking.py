"""add  completed_at to Booking

Revision ID: 916963bf22e1
Revises: 42cd3bb3067b
Create Date: 2024-02-17 01:10:34.530571

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '916963bf22e1'
down_revision: Union[str, None] = '42cd3bb3067b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add columns 'completed_at' and 'is_completed'
    op.alter_column('bookings', sa.Column('completed_at', sa.TIMESTAMP(timezone=True), nullable=True))

def downgrade() -> None:
    # Drop columns 'completed_at' and 'is_completed'
    op.drop_column('bookings', 'completed_at')
