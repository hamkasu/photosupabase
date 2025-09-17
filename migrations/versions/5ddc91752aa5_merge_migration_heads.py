"""merge migration heads

Revision ID: 5ddc91752aa5
Revises: 001_complete_schema_initial, 304d3e98ef6d
Create Date: 2025-09-15 07:14:38.943470

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5ddc91752aa5'
down_revision = ('001_complete_schema_initial', '304d3e98ef6d')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
