"""Document and version models (quotations, 2D/3D drawings, schedules)."""

import enum
import uuid

from sqlalchemy import BigInteger, ForeignKey, Integer, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class DocumentType(str, enum.Enum):
    QUOTATION = "QUOTATION"
    DRAWING_2D = "DRAWING_2D"
    DRAWING_3D = "DRAWING_3D"
    MODEL_3D = "MODEL_3D"  # glTF/GLB model for in-app 3D viewing
    SCHEDULE = "SCHEDULE"
    OTHER = "OTHER"


class Document(Base):
    __tablename__ = "documents"

    job_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type: Mapped[DocumentType] = mapped_column(
        SAEnum(DocumentType, name="document_type"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    current_version_no: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    versions: Mapped[list["DocumentVersion"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
        order_by="DocumentVersion.version_no",
    )


class DocumentVersion(Base):
    __tablename__ = "document_versions"

    document_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version_no: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_key: Mapped[str] = mapped_column(String(500), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(120), nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    uploaded_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)

    document: Mapped[Document] = relationship(back_populates="versions")
