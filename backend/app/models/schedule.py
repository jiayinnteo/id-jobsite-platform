"""Scheduling models: site visits, schedule items, calendar links."""

import enum
import uuid
from datetime import date, datetime, time

from sqlalchemy import Date, DateTime, ForeignKey, String, Time, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class VisitStatus(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class SiteVisit(Base):
    __tablename__ = "site_visits"

    job_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    rectification_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("rectifications.id", ondelete="SET NULL"), nullable=True
    )
    contractor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    scheduled_date: Mapped[date] = mapped_column(Date, nullable=False)
    scheduled_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    status: Mapped[VisitStatus] = mapped_column(
        SAEnum(VisitStatus, name="visit_status"),
        default=VisitStatus.SCHEDULED,
        nullable=False,
    )
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)

    workers: Mapped[list["VisitWorker"]] = relationship(
        back_populates="visit", cascade="all, delete-orphan"
    )


class VisitWorker(Base):
    __tablename__ = "visit_workers"
    __table_args__ = (
        UniqueConstraint("site_visit_id", "worker_id", name="uq_visit_worker"),
    )

    site_visit_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("site_visits.id", ondelete="CASCADE"), nullable=False, index=True
    )
    worker_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)

    visit: Mapped[SiteVisit] = relationship(back_populates="workers")


class CalendarLink(Base):
    """Stores a user's Google Calendar connection + sync state."""

    __tablename__ = "calendar_links"
    __table_args__ = (UniqueConstraint("user_id", name="uq_calendar_user"),)

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    google_calendar_id: Mapped[str | None] = mapped_column(String(200), nullable=True)
    access_token: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    refresh_token: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    sync_token: Mapped[str | None] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="CONNECTED", nullable=False)


class CalendarEventLink(Base):
    """Maps a (schedule entity, user) pair to the Google event id for idempotent
    updates — enables per-participant auto-linking."""

    __tablename__ = "calendar_event_links"
    __table_args__ = (
        UniqueConstraint(
            "entity_type", "entity_id", "user_id", name="uq_cal_event_link"
        ),
    )

    entity_type: Mapped[str] = mapped_column(String(40), nullable=False)  # site_visit
    entity_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    google_event_id: Mapped[str | None] = mapped_column(String(256), nullable=True)
    last_synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
