"""Add schema

Revision ID: 43fb18a1a53b
Revises: 64254d2cc72b
Create Date: 2023-01-30 15:00:55.952600

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '43fb18a1a53b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute("CREATE SCHEMA IF NOT EXISTS indice_schema;")
    


def downgrade():
    connection = op.get_bind()
    connection.execute("DROP SCHEMA IF EXISTS indice_schema;")
