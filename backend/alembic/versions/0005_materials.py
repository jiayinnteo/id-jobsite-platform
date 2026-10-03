"""material suppliers, products, selections; add MODEL_3D document type

Revision ID: 0005_materials
Revises: 0004_chat_ai
Create Date: 2026-10-03
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0005_materials"
down_revision: str | None = "0004_chat_ai"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

supplier_country = sa.Enum("SG", "MY", name="supplier_country")
material_category = sa.Enum(
    "LAMINATE", "TILE", "WORKTOP", "PAINT", "VINYL", "FLOORING", "OTHER",
    name="material_category",
)
selection_status = sa.Enum(
    "PROPOSED", "APPROVED", "CHANGE_REQUESTED", name="selection_status"
)


def _ts():
    return sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now())


def upgrade() -> None:
    bind = op.get_bind()
    for enum in (supplier_country, material_category, selection_status):
        enum.create(bind, checkfirst=True)

    # Add MODEL_3D to the existing document_type enum (Postgres).
    op.execute("ALTER TYPE document_type ADD VALUE IF NOT EXISTS 'MODEL_3D'")

    op.create_table(
        "material_suppliers",
        sa.Column("id", sa.Uuid(), primary_key=True),
        _ts(),
        sa.Column("key", sa.String(60), nullable=False, unique=True),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("country", supplier_country, nullable=False),
        sa.Column("website_url", sa.String(400)),
    )

    op.create_table(
        "material_products",
        sa.Column("id", sa.Uuid(), primary_key=True),
        _ts(),
        sa.Column("supplier_id", sa.Uuid(), sa.ForeignKey("material_suppliers.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("category", material_category, nullable=False, index=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("product_code", sa.String(80)),
        sa.Column("colour", sa.String(120)),
        sa.Column("colour_hex", sa.String(9)),
        sa.Column("finish", sa.String(120)),
        sa.Column("swatch_url", sa.String(600)),
        sa.Column("source_url", sa.String(600)),
    )

    op.create_table(
        "material_selections",
        sa.Column("id", sa.Uuid(), primary_key=True),
        _ts(),
        sa.Column("job_id", sa.Uuid(), sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("product_id", sa.Uuid(), sa.ForeignKey("material_products.id", ondelete="SET NULL")),
        sa.Column("category", material_category, nullable=False),
        sa.Column("area", sa.String(160)),
        sa.Column("colour", sa.String(120)),
        sa.Column("colour_hex", sa.String(9)),
        sa.Column("note", sa.Text()),
        sa.Column("status", selection_status, nullable=False),
        sa.Column("selected_by", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
    )


def downgrade() -> None:
    for table in ("material_selections", "material_products", "material_suppliers"):
        op.drop_table(table)
    bind = op.get_bind()
    for enum in (selection_status, material_category, supplier_country):
        enum.drop(bind, checkfirst=True)
    # Note: Postgres cannot easily remove an enum value; MODEL_3D is left in place.
