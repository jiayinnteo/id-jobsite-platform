"""initial: companies and users

Revision ID: 0001_initial
Revises:
Create Date: 2026-10-03
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "companies",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column(
            "type",
            sa.Enum("ID_FIRM", "CONTRACTOR", name="company_type"),
            nullable=False,
        ),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=200), nullable=False),
        sa.Column(
            "role",
            sa.Enum("ID_BOSS", "ID", "CLIENT", "CONTRACTOR", "WORKER", name="user_role"),
            nullable=False,
        ),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("company_id", sa.Uuid(), sa.ForeignKey("companies.id"), nullable=True),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    op.drop_table("companies")
    sa.Enum(name="user_role").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="company_type").drop(op.get_bind(), checkfirst=True)
