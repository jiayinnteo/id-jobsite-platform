"""add swatch_url to material_selections (texture preview)

Revision ID: 0007_selection_swatch
Revises: 0006_material_surface
Create Date: 2026-10-03
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0007_selection_swatch"
down_revision: str | None = "0006_material_surface"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "material_selections",
        sa.Column("swatch_url", sa.String(600), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("material_selections", "swatch_url")
