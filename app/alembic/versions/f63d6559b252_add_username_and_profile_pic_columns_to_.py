"""Add username and profile_pic columns to users table

Revision ID: f63d6559b252
Revises: 0ab6b0b918e9
Create Date: 2024-05-17 13:14:00.309679

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f63d6559b252'
down_revision: Union[str, None] = '0ab6b0b918e9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add username column to users table
    op.add_column('users', sa.Column('username', sa.String(), nullable=True))
    
    # Add profile_pic column to users table
    op.add_column('users', sa.Column('profile_pic', sa.String(), nullable=True))


def downgrade():
    # Remove profile_pic column from users table
    op.drop_column('users', 'profile_pic')
    
    # Remove username column from users table
    op.drop_column('users', 'username')