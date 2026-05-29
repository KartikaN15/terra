"""Add GWP/region/unit audit columns to activity_events and gwp_version to emission_factors.

Revision ID: a1b2c3d4e5f6
Revises: e65edce0b27f
Create Date: 2026-05-07
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "e65edce0b27f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("activity_events") as batch:
        batch.add_column(sa.Column("gwp_version", sa.String(length=20), nullable=True))
        batch.add_column(sa.Column("region_match", sa.String(length=20), nullable=True))
        batch.add_column(sa.Column("unit_converted", sa.Boolean(), nullable=True, server_default=sa.false()))

    with op.batch_alter_table("emission_factors") as batch:
        batch.add_column(sa.Column("gwp_version", sa.String(length=20), nullable=True, server_default="AR5"))


def downgrade() -> None:
    with op.batch_alter_table("emission_factors") as batch:
        batch.drop_column("gwp_version")
    with op.batch_alter_table("activity_events") as batch:
        batch.drop_column("unit_converted")
        batch.drop_column("region_match")
        batch.drop_column("gwp_version")
