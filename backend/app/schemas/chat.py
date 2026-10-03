"""Schemas for conversations and messages."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.chat import Channel, MessageDirection


class MessageCreate(BaseModel):
    body: str = Field(min_length=1, max_length=4000)
    attachment_ref: str | None = Field(default=None, max_length=500)
    linked_entity: str | None = Field(default=None, max_length=120)


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    conversation_id: uuid.UUID
    channel: Channel
    direction: MessageDirection
    sender_id: uuid.UUID | None
    body: str
    attachment_ref: str | None
    linked_entity: str | None
    created_at: datetime


class ConversationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    job_id: uuid.UUID
    created_at: datetime
