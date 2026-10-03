"""Defect, rectification-decision and photo endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.base import get_db
from app.models.user import User
from app.schemas.defect import (
    DecisionRequest,
    DefectAssign,
    DefectCreate,
    DefectHistoryOut,
    DefectOut,
    DefectStatusUpdate,
    PhotoCreate,
    PhotoOut,
    PhotoUploadTarget,
    RectificationOut,
)
from app.services import defect_service

job_defects_router = APIRouter(prefix="/jobs", tags=["defects"])
defects_router = APIRouter(prefix="/defects", tags=["defects"])
rect_router = APIRouter(prefix="/rectifications", tags=["defects"])


@job_defects_router.post(
    "/{job_id}/defects", response_model=DefectOut, status_code=status.HTTP_201_CREATED
)
async def create_defect(
    job_id: uuid.UUID,
    data: DefectCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await defect_service.create_defect(db, user, job_id, data)


@job_defects_router.get("/{job_id}/defects", response_model=list[DefectOut])
async def list_defects(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await defect_service.list_defects(db, user, job_id)


@defects_router.get("/{defect_id}", response_model=DefectOut)
async def get_defect(
    defect_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await defect_service.get_defect(db, user, defect_id)


@defects_router.get("/{defect_id}/history", response_model=list[DefectHistoryOut])
async def get_history(
    defect_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await defect_service.get_history(db, user, defect_id)


@defects_router.post("/{defect_id}/assign", response_model=DefectOut)
async def assign_defect(
    defect_id: uuid.UUID,
    data: DefectAssign,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await defect_service.assign_defect(db, user, defect_id, data)


@defects_router.patch("/{defect_id}/status", response_model=DefectOut)
async def update_status(
    defect_id: uuid.UUID,
    data: DefectStatusUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await defect_service.update_status(db, user, defect_id, data)


@rect_router.post("/{rectification_id}/decision", response_model=RectificationOut)
async def decide(
    rectification_id: uuid.UUID,
    data: DecisionRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await defect_service.decide_rectification(db, user, rectification_id, data)


# --- Photos ---


@job_defects_router.post(
    "/{job_id}/photos", response_model=PhotoUploadTarget, status_code=status.HTTP_201_CREATED
)
async def create_photo(
    job_id: uuid.UUID,
    data: PhotoCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    photo, upload_url = await defect_service.create_photo(db, user, job_id, data)
    return PhotoUploadTarget(
        photo_id=photo.id, storage_key=photo.storage_key, upload_url=upload_url
    )


@job_defects_router.get("/{job_id}/photos", response_model=list[PhotoOut])
async def list_photos(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    photos = await defect_service.list_photos(db, user, job_id)
    out = []
    for p in photos:
        item = PhotoOut.model_validate(p)
        item.download_url = defect_service.photo_download_url(p)
        out.append(item)
    return out
