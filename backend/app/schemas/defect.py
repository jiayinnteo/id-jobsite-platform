"""Schemas for defects, rectification decisions and photos."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.defect import DefectStatus, RectificationDecision


class DefectCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=4000)
    location: str | None = Field(default=None, max_length=200)


class DefectAssign(BaseModel):
    contractor_id: uuid.UUID


class DefectStatusUpdate(BaseModel):
    to_status: DefectStatus
    reason: str | None = Field(default=None, max_length=2000)


class DefectHistoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    from_status: DefectStatus | None
    to_status: DefectStatus
    changed_by: uuid.UUID
    reason: str | None
    created_at: datetime


class DefectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    job_id: uuid.UUID
    title: str
    description: str | None
    location: str | None
    status: DefectStatus
    created_by: uuid.UUID
    assigned_contractor_id: uuid.UUID | None
    created_at: datetime
    rectification_id: uuid.UUID | None = None


class DecisionRequest(BaseModel):
    decision: RectificationDecision
    reason: str | None = Field(default=None, max_length=2000)


class RectificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    defect_id: uuid.UUID
    decision: RectificationDecision | None
    reason: str | None


# --- Photos ---

class PhotoCreate(BaseModel):
    filename: str = Field(min_length=1, max_length=200)
    mime_type: str
    size_bytes: int = Field(ge=1)
    caption: str | None = Field(default=None, max_length=400)
    defect_id: uuid.UUID | None = None


class PhotoUploadTarget(BaseModel):
    photo_id: uuid.UUID
    storage_key: str
    upload_url: str


class PhotoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    job_id: uuid.UUID
    defect_id: uuid.UUID | None
    caption: str | None
    uploaded_by: uuid.UUID
    created_at: datetime
    download_url: str | None = None
