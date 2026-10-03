"""device push-token registrations

Revision ID: 0008_device_tokens
Revises: 0007_selection_swatch
Create Date: 2026-10-03
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0008_device_tokens"
down_revision: str | None = "0007_selection_swatch"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

device_platform = sa.Enum("ANDROID", "IOS", "WEB", name="device_platform")


def upgrade() -> None:
    device_platform.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "device_tokens",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("token", sa.String(512), nullable=False),
        sa.Column("platform", device_platform, nullable=False),
        sa.UniqueConstraint("token", name="uq_device_token"),
    )


def downgrade() -> None:
    op.drop_table("device_tokens")
    device_platform.drop(op.get_bind(), checkfirst=True)
