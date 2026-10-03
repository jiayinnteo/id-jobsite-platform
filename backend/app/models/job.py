"""Job / project models, membership, boss oversight and client reviews."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.user import UserRole


class JobStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    ON_HOLD = "ON_HOLD"
    COMPLETED = "COMPLETED"


class Job(Base):
    __tablename__ = "jobs"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    address: Mapped[str] = mapped_column(String(400), nullable=False)
    status: Mapped[JobStatus] = mapped_column(
        SAEnum(JobStatus, name="job_status"), default=JobStatus.DRAFT, nullable=False
    )
    # The ID firm that owns the job — enables ID_BOSS firm-wide oversight.
    firm_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("companies.id"), nullable=True, index=True
    )
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    client_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    members: Mapped[list["JobMember"]] = relationship(
        back_populates="job", cascade="all, delete-orphan"
    )


class JobMember(Base):
    __tablename__ = "job_members"
    __table_args__ = (UniqueConstraint("job_id", "user_id", name="uq_job_member"),)

    job_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    role_in_job: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="user_role", create_type=False), nullable=False
    )

    job: Mapped[Job] = relationship(back_populates="members")


class OversightFlag(str, enum.Enum):
    NEEDS_ATTENTION = "NEEDS_ATTENTION"
    APPROVED = "APPROVED"


class OversightReview(Base):
    """Internal, firm-only review by an ID_BOSS. Never shown to client/contractor."""

    __tablename__ = "oversight_reviews"

    job_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    boss_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    flag: Mapped[OversightFlag] = mapped_column(
        SAEnum(OversightFlag, name="oversight_flag"), nullable=False
    )
    note: Mapped[str | None] = mapped_column(Text, nullable=True)


class JobReview(Base):
    """Client-facing review/rating of a completed job."""

    __tablename__ = "job_reviews"
    __table_args__ = (UniqueConstraint("job_id", "client_id", name="uq_job_review"),)

    job_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1..5
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )
