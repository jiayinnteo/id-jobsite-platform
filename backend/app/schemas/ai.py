"""Schemas for AI drafts (human-in-the-loop)."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.chat import DraftStatus


class DraftGenerateRequest(BaseModel):
    conversation_id: uuid.UUID


class DraftEdit(BaseModel):
    edited_text: str = Field(min_length=1, max_length=4000)


class AIDraftOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    conversation_id: uuid.UUID
    draft_text: str
    edited_text: str | None
    status: DraftStatus
    reviewed_by: uuid.UUID | None
    created_at: datetime
