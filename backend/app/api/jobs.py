"""Job, member, oversight-review and client-review endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_roles
from app.core.errors import ForbiddenError
from app.db.base import get_db
from app.models.user import User, UserRole
from app.schemas.job import (
    JobCreate,
    JobMemberAdd,
    JobOut,
    JobReviewOut,
    JobReviewUpsert,
    JobUpdate,
    OversightReviewCreate,
    OversightReviewOut,
)
from app.services import job_service

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobOut, status_code=status.HTTP_201_CREATED)
async def create_job(
    data: JobCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles(UserRole.ID, UserRole.ID_BOSS)),
):
    return await job_service.create_job(db, user, data)


@router.get("", response_model=list[JobOut])
async def list_jobs(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await job_service.list_jobs_for_user(db, user)


@router.get("/{job_id}", response_model=JobOut)
async def get_job(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await job_service.get_job(db, user, job_id)


@router.patch("/{job_id}", response_model=JobOut)
async def update_job(
    job_id: uuid.UUID,
    data: JobUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await job_service.update_job(db, user, job_id, data)


@router.post("/{job_id}/members", response_model=JobOut, status_code=status.HTTP_201_CREATED)
async def add_member(
    job_id: uuid.UUID,
    data: JobMemberAdd,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await job_service.add_member(db, user, job_id, data)
    return await job_service.get_job(db, user, job_id)


@router.post(
    "/{job_id}/oversight-reviews",
    response_model=OversightReviewOut,
    status_code=status.HTTP_201_CREATED,
)
async def add_oversight_review(
    job_id: uuid.UUID,
    data: OversightReviewCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles(UserRole.ID_BOSS)),
):
    return await job_service.add_oversight_review(db, user, job_id, data)


@router.post("/{job_id}/review", response_model=JobReviewOut)
async def upsert_review(
    job_id: uuid.UUID,
    data: JobReviewUpsert,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await job_service.upsert_job_review(db, user, job_id, data)


@router.get("/{job_id}/review", response_model=JobReviewOut)
async def get_review(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await job_service.get_job_review(db, user, job_id)


firm_router = APIRouter(prefix="/firm", tags=["firm"])


@firm_router.get("/ratings")
async def firm_ratings(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles(UserRole.ID, UserRole.ID_BOSS)),
):
    if user.company_id is None:
        raise ForbiddenError("You are not part of a firm.", code="no_firm")
    return await job_service.firm_average_rating(db, user.company_id)
