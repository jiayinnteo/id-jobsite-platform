"""site visits, visit workers, calendar links

Revision ID: 0003_scheduling
Revises: 0002_jobs_docs_defects
Create Date: 2026-10-03
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0003_scheduling"
down_revision: str | None = "0002_jobs_docs_defects"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

visit_status = sa.Enum("SCHEDULED", "COMPLETED", "CANCELLED", name="visit_status")


def _ts():
    return sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now())


def upgrade() -> None:
    visit_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "site_visits",
        sa.Column("id", sa.Uuid(), primary_key=True),
        _ts(),
        sa.Column("job_id", sa.Uuid(), sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("rectification_id", sa.Uuid(), sa.ForeignKey("rectifications.id", ondelete="SET NULL")),
        sa.Column("contractor_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("scheduled_date", sa.Date(), nullable=False),
        sa.Column("scheduled_time", sa.Time()),
        sa.Column("status", visit_status, nullable=False),
        sa.Column("created_by", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
    )

    op.create_table(
        "visit_workers",
        sa.Column("id", sa.Uuid(), primary_key=True),
        _ts(),
        sa.Column("site_visit_id", sa.Uuid(), sa.ForeignKey("site_visits.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("worker_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.UniqueConstraint("site_visit_id", "worker_id", name="uq_visit_worker"),
    )

    op.create_table(
        "calendar_links",
        sa.Column("id", sa.Uuid(), primary_key=True),
        _ts(),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("google_calendar_id", sa.String(200)),
        sa.Column("access_token", sa.String(2048)),
        sa.Column("refresh_token", sa.String(2048)),
        sa.Column("sync_token", sa.String(512)),
        sa.Column("status", sa.String(32), nullable=False, server_default="CONNECTED"),
        sa.UniqueConstraint("user_id", name="uq_calendar_user"),
    )

    op.create_table(
        "calendar_event_links",
        sa.Column("id", sa.Uuid(), primary_key=True),
        _ts(),
        sa.Column("entity_type", sa.String(40), nullable=False),
        sa.Column("entity_id", sa.Uuid(), nullable=False, index=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("google_event_id", sa.String(256)),
        sa.Column("last_synced_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("entity_type", "entity_id", "user_id", name="uq_cal_event_link"),
    )


def downgrade() -> None:
    for table in ("calendar_event_links", "calendar_links", "visit_workers", "site_visits"):
        op.drop_table(table)
    visit_status.drop(op.get_bind(), checkfirst=True)
