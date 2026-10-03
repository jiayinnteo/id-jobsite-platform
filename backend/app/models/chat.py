"""Conversation, message, read-state and AI-draft models (chat + WhatsApp)."""

import enum
import uuid

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Channel(str, enum.Enum):
    IN_APP = "IN_APP"
    WHATSAPP = "WHATSAPP"


class MessageDirection(str, enum.Enum):
    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"


class Conversation(Base):
    """One conversation per job, spanning in-app chat and WhatsApp."""

    __tablename__ = "conversations"
    __table_args__ = (UniqueConstraint("job_id", name="uq_conversation_job"),)

    job_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )

    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )


class Message(Base):
    __tablename__ = "messages"
    __table_args__ = (
        # De-dup bridged messages by channel + external id.
        UniqueConstraint("channel", "external_id", name="uq_message_external"),
    )

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    channel: Mapped[Channel] = mapped_column(
        SAEnum(Channel, name="message_channel"), default=Channel.IN_APP, nullable=False
    )
    direction: Mapped[MessageDirection] = mapped_column(
        SAEnum(MessageDirection, name="message_direction"), nullable=False
    )
    sender_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    body: Mapped[str] = mapped_column(Text, nullable=False)
    attachment_ref: Mapped[str | None] = mapped_column(String(500), nullable=True)
    linked_entity: Mapped[str | None] = mapped_column(String(120), nullable=True)
    external_id: Mapped[str | None] = mapped_column(String(200), nullable=True)

    conversation: Mapped[Conversation] = relationship(back_populates="messages")


class MessageRead(Base):
    __tablename__ = "message_reads"
    __table_args__ = (
        UniqueConstraint("message_id", "user_id", name="uq_message_read"),
    )

    message_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("messages.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)


class DraftStatus(str, enum.Enum):
    PENDING_REVIEW = "PENDING_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    SENT = "SENT"


class AIDraft(Base):
    """An AI-generated reply awaiting human review (human-in-the-loop)."""

    __tablename__ = "ai_drafts"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    message_context: Mapped[str | None] = mapped_column(Text, nullable=True)
    draft_text: Mapped[str] = mapped_column(Text, nullable=False)
    edited_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[DraftStatus] = mapped_column(
        SAEnum(DraftStatus, name="draft_status"),
        default=DraftStatus.PENDING_REVIEW,
        nullable=False,
    )
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
