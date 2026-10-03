"""add model_surface to material_selections (3D preview mapping)

Revision ID: 0006_material_surface
Revises: 0005_materials
Create Date: 2026-10-03
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0006_material_surface"
down_revision: str | None = "0005_materials"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "material_selections",
        sa.Column("model_surface", sa.String(160), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("material_selections", "model_surface")
