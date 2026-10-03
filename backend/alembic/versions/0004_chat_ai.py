"""conversations, messages, reads, ai drafts

Revision ID: 0004_chat_ai
Revises: 0003_scheduling
Create Date: 2026-10-03
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0004_chat_ai"
down_revision: str | None = "0003_scheduling"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

channel = sa.Enum("IN_APP", "WHATSAPP", name="message_channel")
direction = sa.Enum("INBOUND", "OUTBOUND", name="message_direction")
draft_status = sa.Enum(
    "PENDING_REVIEW", "APPROVED", "REJECTED", "SENT", name="draft_status"
)


def _ts():
    return sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now())


def upgrade() -> None:
    bind = op.get_bind()
    for enum in (channel, direction, draft_status):
        enum.create(bind, checkfirst=True)

    op.create_table(
        "conversations",
        sa.Column("id", sa.Uuid(), primary_key=True),
        _ts(),
        sa.Column("job_id", sa.Uuid(), sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.UniqueConstraint("job_id", name="uq_conversation_job"),
    )

    op.create_table(
        "messages",
        sa.Column("id", sa.Uuid(), primary_key=True),
        _ts(),
        sa.Column("conversation_id", sa.Uuid(), sa.ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("channel", channel, nullable=False),
        sa.Column("direction", direction, nullable=False),
        sa.Column("sender_id", sa.Uuid(), sa.ForeignKey("users.id")),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("attachment_ref", sa.String(500)),
        sa.Column("linked_entity", sa.String(120)),
        sa.Column("external_id", sa.String(200)),
        sa.UniqueConstraint("channel", "external_id", name="uq_message_external"),
    )

    op.create_table(
        "message_reads",
        sa.Column("id", sa.Uuid(), primary_key=True),
        _ts(),
        sa.Column("message_id", sa.Uuid(), sa.ForeignKey("messages.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.UniqueConstraint("message_id", "user_id", name="uq_message_read"),
    )

    op.create_table(
        "ai_drafts",
        sa.Column("id", sa.Uuid(), primary_key=True),
        _ts(),
        sa.Column("conversation_id", sa.Uuid(), sa.ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("message_context", sa.Text()),
        sa.Column("draft_text", sa.Text(), nullable=False),
        sa.Column("edited_text", sa.Text()),
        sa.Column("status", draft_status, nullable=False),
        sa.Column("reviewed_by", sa.Uuid(), sa.ForeignKey("users.id")),
    )


def downgrade() -> None:
    for table in ("ai_drafts", "message_reads", "messages", "conversations"):
        op.drop_table(table)
    bind = op.get_bind()
    for enum in (draft_status, direction, channel):
        enum.drop(bind, checkfirst=True)
