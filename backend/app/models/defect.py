"""Defect, status history, rectification, decision and photo models."""

import enum
import uuid

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class DefectStatus(str, enum.Enum):
    OPEN = "OPEN"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    RECTIFIED = "RECTIFIED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    CLOSED = "CLOSED"


# Allowed transitions enforced by the service layer.
ALLOWED_TRANSITIONS: dict[DefectStatus, set[DefectStatus]] = {
    DefectStatus.OPEN: {DefectStatus.ASSIGNED},
    DefectStatus.ASSIGNED: {DefectStatus.IN_PROGRESS},
    DefectStatus.IN_PROGRESS: {DefectStatus.RECTIFIED},
    DefectStatus.RECTIFIED: {DefectStatus.ACCEPTED, DefectStatus.REJECTED},
    DefectStatus.REJECTED: {DefectStatus.ASSIGNED},
    DefectStatus.ACCEPTED: {DefectStatus.CLOSED},
    DefectStatus.CLOSED: set(),
}


class Defect(Base):
    __tablename__ = "defects"

    job_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    status: Mapped[DefectStatus] = mapped_column(
        SAEnum(DefectStatus, name="defect_status"),
        default=DefectStatus.OPEN,
        nullable=False,
    )
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    assigned_contractor_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )

    history: Mapped[list["DefectStatusHistory"]] = relationship(
        back_populates="defect", cascade="all, delete-orphan"
    )
    photos: Mapped[list["Photo"]] = relationship(back_populates="defect")


class DefectStatusHistory(Base):
    __tablename__ = "defect_status_history"

    defect_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("defects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    from_status: Mapped[DefectStatus | None] = mapped_column(
        SAEnum(DefectStatus, name="defect_status", create_type=False), nullable=True
    )
    to_status: Mapped[DefectStatus] = mapped_column(
        SAEnum(DefectStatus, name="defect_status", create_type=False), nullable=False
    )
    changed_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    defect: Mapped[Defect] = relationship(back_populates="history")


class RectificationDecision(str, enum.Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class Rectification(Base):
    __tablename__ = "rectifications"

    defect_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("defects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    contractor_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    # Set once the client decides.
    decision: Mapped[RectificationDecision | None] = mapped_column(
        SAEnum(RectificationDecision, name="rectification_decision"), nullable=True
    )
    decided_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)


class Photo(Base):
    __tablename__ = "photos"

    job_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    defect_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("defects.id", ondelete="SET NULL"), nullable=True, index=True
    )
    storage_key: Mapped[str] = mapped_column(String(500), nullable=False)
    caption: Mapped[str | None] = mapped_column(String(400), nullable=True)
    uploaded_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)

    defect: Mapped[Defect | None] = relationship(back_populates="photos")
