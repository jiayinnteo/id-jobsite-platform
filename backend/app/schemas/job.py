"""Schemas for jobs, members, oversight reviews and client reviews."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.job import JobStatus, OversightFlag
from app.models.user import UserRole


class JobCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    address: str = Field(min_length=1, max_length=400)
    client_id: uuid.UUID | None = None


class JobUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    address: str | None = Field(default=None, max_length=400)
    status: JobStatus | None = None


class JobMemberAdd(BaseModel):
    user_id: uuid.UUID
    role_in_job: UserRole


class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    address: str
    status: JobStatus
    firm_id: uuid.UUID | None = None
    created_by: uuid.UUID
    client_id: uuid.UUID | None = None
    created_at: datetime


class OversightReviewCreate(BaseModel):
    flag: OversightFlag
    note: str | None = Field(default=None, max_length=2000)


class OversightReviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    job_id: uuid.UUID
    boss_id: uuid.UUID
    flag: OversightFlag
    note: str | None
    created_at: datetime


class JobReviewUpsert(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=2000)


class JobReviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    job_id: uuid.UUID
    client_id: uuid.UUID
    rating: int
    comment: str | None
    created_at: datetime
    updated_at: datetime | None = None
