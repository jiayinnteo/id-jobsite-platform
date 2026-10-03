"""Schemas for site visits and contractor work."""

import uuid
from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, Field

from app.models.schedule import VisitStatus


class SiteVisitCreate(BaseModel):
    rectification_id: uuid.UUID | None = None
    scheduled_date: date
    scheduled_time: time | None = None
    worker_ids: list[uuid.UUID] = Field(default_factory=list)


class SiteVisitUpdate(BaseModel):
    scheduled_date: date | None = None
    scheduled_time: time | None = None
    status: VisitStatus | None = None
    worker_ids: list[uuid.UUID] | None = None


class SiteVisitOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    job_id: uuid.UUID
    rectification_id: uuid.UUID | None
    contractor_id: uuid.UUID
    scheduled_date: date
    scheduled_time: time | None
    status: VisitStatus
    created_at: datetime
    worker_ids: list[uuid.UUID] = Field(default_factory=list)


class ContractorWorkItem(BaseModel):
    """A rectification assigned to the contractor, with its defect context."""

    rectification_id: uuid.UUID
    defect_id: uuid.UUID
    job_id: uuid.UUID
    defect_title: str
    defect_status: str
