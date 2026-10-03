"""jobs, documents, defects, photos, reviews, notifications, audit

Revision ID: 0002_jobs_docs_defects
Revises: 0001_initial
Create Date: 2026-10-03
"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0002_jobs_docs_defects"
down_revision: str | None = "0001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# user_role already exists from 0001; reference it without recreating.
user_role = postgresql.ENUM(
    "ID_BOSS", "ID", "CLIENT", "CONTRACTOR", "WORKER", name="user_role", create_type=False
)
job_status = sa.Enum("DRAFT", "ACTIVE", "ON_HOLD", "COMPLETED", name="job_status")
oversight_flag = sa.Enum("NEEDS_ATTENTION", "APPROVED", name="oversight_flag")
document_type = sa.Enum(
    "QUOTATION", "DRAWING_2D", "DRAWING_3D", "SCHEDULE", "OTHER", name="document_type"
)
defect_status = sa.Enum(
    "OPEN", "ASSIGNED", "IN_PROGRESS", "RECTIFIED", "ACCEPTED", "REJECTED", "CLOSED",
    name="defect_status",
)
rectification_decision = sa.Enum(
    "ACCEPTED", "REJECTED", name="rectification_decision"
)

def _ts():
    return sa.Column(
        "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
    )


def upgrade() -> None:
    bind = op.get_bind()
    for enum in (job_status, oversight_flag, document_type, defect_status, rectification_decision):
        enum.create(bind, checkfirst=True)

    op.create_table(
        "jobs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        _ts(),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("address", sa.String(400), nullable=False),
        sa.Column("status", job_status, nullable=False),
        sa.Column("firm_id", sa.Uuid(), sa.ForeignKey("companies.id"), index=True),
        sa.Column("created_by", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("client_id", sa.Uuid(), sa.ForeignKey("users.id")),
    )

    op.create_table(
        "job_members",
        sa.Column("id", sa.Uuid(), primary_key=True),
        _ts(),
        sa.Column("job_id", sa.Uuid(), sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("role_in_job", user_role, nullable=False),
        sa.UniqueConstraint("job_id", "user_id", name="uq_job_member"),
    )

    op.create_table(
        "oversight_reviews",
        sa.Column("id", sa.Uuid(), primary_key=True),
        _ts(),
        sa.Column("job_id", sa.Uuid(), sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("boss_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("flag", oversight_flag, nullable=False),
        sa.Column("note", sa.Text()),
    )

    op.create_table(
        "job_reviews",
        sa.Column("id", sa.Uuid(), primary_key=True),
        _ts(),
        sa.Column("job_id", sa.Uuid(), sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("client_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text()),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("job_id", "client_id", name="uq_job_review"),
    )

    op.create_table(
        "documents",
        sa.Column("id", sa.Uuid(), primary_key=True),
        _ts(),
        sa.Column("job_id", sa.Uuid(), sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("type", document_type, nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("created_by", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("current_version_no", sa.Integer(), nullable=False, server_default="0"),
    )

    op.create_table(
        "document_versions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        _ts(),
        sa.Column("document_id", sa.Uuid(), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("version_no", sa.Integer(), nullable=False),
        sa.Column("storage_key", sa.String(500), nullable=False),
        sa.Column("mime_type", sa.String(120), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("uploaded_by", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
    )

    op.create_table(
        "defects",
        sa.Column("id", sa.Uuid(), primary_key=True),
        _ts(),
        sa.Column("job_id", sa.Uuid(), sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("location", sa.String(200)),
        sa.Column("status", defect_status, nullable=False),
        sa.Column("created_by", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("assigned_contractor_id", sa.Uuid(), sa.ForeignKey("users.id")),
    )

    op.create_table(
        "defect_status_history",
        sa.Column("id", sa.Uuid(), primary_key=True),
        _ts(),
        sa.Column("defect_id", sa.Uuid(), sa.ForeignKey("defects.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("from_status", defect_status, nullable=True),
        sa.Column("to_status", defect_status, nullable=False),
        sa.Column("changed_by", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("reason", sa.Text()),
    )

    op.create_table(
        "rectifications",
        sa.Column("id", sa.Uuid(), primary_key=True),
        _ts(),
        sa.Column("defect_id", sa.Uuid(), sa.ForeignKey("defects.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("contractor_id", sa.Uuid(), sa.ForeignKey("users.id")),
        sa.Column("decision", rectification_decision, nullable=True),
        sa.Column("decided_by", sa.Uuid(), sa.ForeignKey("users.id")),
        sa.Column("reason", sa.Text()),
    )

    op.create_table(
        "photos",
        sa.Column("id", sa.Uuid(), primary_key=True),
        _ts(),
        sa.Column("job_id", sa.Uuid(), sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("defect_id", sa.Uuid(), sa.ForeignKey("defects.id", ondelete="SET NULL"), index=True),
        sa.Column("storage_key", sa.String(500), nullable=False),
        sa.Column("caption", sa.String(400)),
        sa.Column("uploaded_by", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
    )

    op.create_table(
        "notifications",
        sa.Column("id", sa.Uuid(), primary_key=True),
        _ts(),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("type", sa.String(80), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("body", sa.Text()),
        sa.Column("deep_link", sa.String(300)),
        sa.Column("read_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        _ts(),
        sa.Column("job_id", sa.Uuid(), sa.ForeignKey("jobs.id", ondelete="SET NULL"), index=True),
        sa.Column("actor_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("action", sa.String(120), nullable=False),
        sa.Column("target_type", sa.String(80), nullable=False),
        sa.Column("target_id", sa.String(80)),
        sa.Column("audit_metadata", postgresql.JSONB()),
    )


def downgrade() -> None:
    for table in (
        "audit_logs", "notifications", "photos", "rectifications",
        "defect_status_history", "defects", "document_versions", "documents",
        "job_reviews", "oversight_reviews", "job_members", "jobs",
    ):
        op.drop_table(table)
    bind = op.get_bind()
    for enum in (rectification_decision, defect_status, document_type, oversight_flag, job_status):
        enum.drop(bind, checkfirst=True)
