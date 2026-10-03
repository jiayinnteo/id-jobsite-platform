"""Site-visit scheduling and contractor/worker queue endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_roles
from app.db.base import get_db
from app.models.user import User, UserRole
from app.schemas.schedule import (
    ContractorWorkItem,
    SiteVisitCreate,
    SiteVisitOut,
    SiteVisitUpdate,
)
from app.services import schedule_service

job_visits_router = APIRouter(prefix="/jobs", tags=["schedule"])
visits_router = APIRouter(prefix="/visits", tags=["schedule"])
contractor_router = APIRouter(prefix="/contractor", tags=["schedule"])
worker_router = APIRouter(prefix="/worker", tags=["schedule"])


@job_visits_router.post(
    "/{job_id}/visits", response_model=SiteVisitOut, status_code=status.HTTP_201_CREATED
)
async def create_visit(
    job_id: uuid.UUID,
    data: SiteVisitCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles(UserRole.CONTRACTOR)),
):
    visit = await schedule_service.create_visit(db, user, job_id, data)
    return schedule_service.visit_to_out_dict(visit)


@job_visits_router.get("/{job_id}/visits", response_model=list[SiteVisitOut])
async def list_visits(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    visits = await schedule_service.list_visits(db, user, job_id)
    return [schedule_service.visit_to_out_dict(v) for v in visits]


@visits_router.patch("/{visit_id}", response_model=SiteVisitOut)
async def update_visit(
    visit_id: uuid.UUID,
    data: SiteVisitUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    visit = await schedule_service.update_visit(db, user, visit_id, data)
    return schedule_service.visit_to_out_dict(visit)


@contractor_router.get("/work", response_model=list[ContractorWorkItem])
async def contractor_work(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles(UserRole.CONTRACTOR)),
):
    return await schedule_service.contractor_work_queue(db, user)


@worker_router.get("/visits", response_model=list[SiteVisitOut])
async def my_visits(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles(UserRole.WORKER)),
):
    visits = await schedule_service.worker_visits(db, user)
    return [schedule_service.visit_to_out_dict(v) for v in visits]
