"""Merge migration heads

Revision ID: ccc2a9758028
Revises: 4ae342c821f6, 4d9b1047e585, 5ddc91752aa5
Create Date: 2025-09-25 11:49:45.741139

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ccc2a9758028'
down_revision = ('4ae342c821f6', '4d9b1047e585', '5ddc91752aa5')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
