"""Ajout UniqueConstraint sur VigilanceMeteo

Revision ID: 510fbdb40b57
Revises: c5d4c9360062
Create Date: 2021-12-02 16:40:34.843480

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '510fbdb40b57'
down_revision = 'c5d4c9360062'
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint('vigilance_meteo_unique_constraint', 'vigilance_meteo', ['zone_id', 'phenomene_id', 'date_export', 'validity'], schema='indice_schema')


def downgrade():
    op.drop_constraint('vigilance_meteo_unique_constraint', 'vigilance_meteo', schema='indice_schema', type_='unique')
