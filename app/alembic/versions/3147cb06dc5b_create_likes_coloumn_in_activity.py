"""create likes coloumn in activity

Revision ID: 3147cb06dc5b
Revises: 
Create Date: 2024-02-05 18:41:49.846686

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3147cb06dc5b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('activities', sa.Column('likes', sa.Integer(), nullable=False, server_default='0'))


def downgrade():
    op.drop_column('activities', 'likes')
