"""Defect tracking, rectification accept/reject, and site photos."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.storage import get_storage
from app.core.config import get_settings
from app.core.errors import AppError, ConflictError, ForbiddenError, NotFoundError
from app.models.defect import (
    ALLOWED_TRANSITIONS,
    Defect,
    DefectStatus,
    DefectStatusHistory,
    Photo,
    Rectification,
    RectificationDecision,
)
from app.models.user import User, UserRole
from app.schemas.defect import (
    DecisionRequest,
    DefectAssign,
    DefectCreate,
    DefectStatusUpdate,
    PhotoCreate,
)
from app.services.common import (
    authorize_job_access,
    get_job_or_404,
    member_user_ids,
    notify,
    write_audit,
)

settings = get_settings()


async def _get_defect(db: AsyncSession, defect_id: uuid.UUID) -> Defect:
    defect = await db.get(Defect, defect_id)
    if not defect:
        raise NotFoundError("Defect not found.", code="defect_not_found")
    return defect


async def create_defect(
    db: AsyncSession, user: User, job_id: uuid.UUID, data: DefectCreate
) -> Defect:
    job = await get_job_or_404(db, job_id)
    await authorize_job_access(db, user, job)

    defect = Defect(
        job_id=job_id, title=data.title, description=data.description,
        location=data.location, status=DefectStatus.OPEN, created_by=user.id,
    )
    db.add(defect)
    await db.flush()
    db.add(
        DefectStatusHistory(
            defect_id=defect.id, from_status=None,
            to_status=DefectStatus.OPEN, changed_by=user.id,
        )
    )
    await notify(
        db, [job.created_by], type="defect.created",
        title=f"New defect: {data.title}", body=data.location,
        deep_link=f"/defects/{defect.id}",
    )
    await write_audit(
        db, actor_id=user.id, action="defect.create", target_type="defect",
        target_id=str(defect.id), job_id=job_id,
    )
    await db.commit()
    await db.refresh(defect)
    return defect


async def list_defects(db: AsyncSession, user: User, job_id: uuid.UUID) -> list[Defect]:
    job = await get_job_or_404(db, job_id)
    await authorize_job_access(db, user, job)
    rows = await db.scalars(select(Defect).where(Defect.job_id == job_id))
    return list(rows.all())


async def get_defect(db: AsyncSession, user: User, defect_id: uuid.UUID) -> Defect:
    defect = await _get_defect(db, defect_id)
    job = await get_job_or_404(db, defect.job_id)
    await authorize_job_access(db, user, job)
    return defect


async def get_history(
    db: AsyncSession, user: User, defect_id: uuid.UUID
) -> list[DefectStatusHistory]:
    await get_defect(db, user, defect_id)
    rows = await db.scalars(
        select(DefectStatusHistory)
        .where(DefectStatusHistory.defect_id == defect_id)
        .order_by(DefectStatusHistory.created_at)
    )
    return list(rows.all())


async def assign_defect(
    db: AsyncSession, user: User, defect_id: uuid.UUID, data: DefectAssign
) -> Defect:
    defect = await _get_defect(db, defect_id)
    job = await get_job_or_404(db, defect.job_id)
    if user.role not in (UserRole.ID, UserRole.ID_BOSS):
        raise ForbiddenError("Only the ID firm can assign defects.", code="id_only")
    await authorize_job_access(db, user, job)

    defect.assigned_contractor_id = data.contractor_id
    await _transition(db, user, defect, DefectStatus.ASSIGNED)
    # Open a rectification record for the accept/reject lifecycle.
    db.add(Rectification(defect_id=defect.id, contractor_id=data.contractor_id))
    await notify(
        db, [data.contractor_id], type="defect.assigned",
        title=f"Defect assigned: {defect.title}", deep_link=f"/defects/{defect.id}",
    )
    await db.commit()
    await db.refresh(defect)
    return defect


async def _transition(
    db: AsyncSession, user: User, defect: Defect, to: DefectStatus, reason: str | None = None
) -> None:
    allowed = ALLOWED_TRANSITIONS.get(defect.status, set())
    if to not in allowed:
        raise ConflictError(
            f"Cannot move defect from {defect.status.value} to {to.value}.",
            code="invalid_transition",
        )
    frm = defect.status
    defect.status = to
    db.add(
        DefectStatusHistory(
            defect_id=defect.id, from_status=frm, to_status=to,
            changed_by=user.id, reason=reason,
        )
    )
    await write_audit(
        db, actor_id=user.id, action="defect.status", target_type="defect",
        target_id=str(defect.id), job_id=defect.job_id,
        metadata={"from": frm.value, "to": to.value},
    )


async def update_status(
    db: AsyncSession, user: User, defect_id: uuid.UUID, data: DefectStatusUpdate
) -> Defect:
    defect = await _get_defect(db, defect_id)
    job = await get_job_or_404(db, defect.job_id)
    await authorize_job_access(db, user, job)

    # Accept/Reject goes through the dedicated decision endpoint.
    if data.to_status in (DefectStatus.ACCEPTED, DefectStatus.REJECTED):
        raise ForbiddenError(
            "Use the accept/reject decision endpoint for client decisions.",
            code="use_decision_endpoint",
        )
    await _transition(db, user, defect, data.to_status, data.reason)
    await notify(
        db, await member_user_ids(db, job), type="defect.status",
        title=f"Defect {data.to_status.value.replace('_', ' ').lower()}: {defect.title}",
        deep_link=f"/defects/{defect.id}",
    )
    await db.commit()
    await db.refresh(defect)
    return defect


async def decide_rectification(
    db: AsyncSession, client: User, rectification_id: uuid.UUID, data: DecisionRequest
) -> Rectification:
    """Client Accept/Reject on rectified work (Requirement 5)."""
    rect = await db.get(Rectification, rectification_id)
    if not rect:
        raise NotFoundError("Rectification not found.", code="rectification_not_found")
    defect = await _get_defect(db, rect.defect_id)
    job = await get_job_or_404(db, defect.job_id)

    if client.id != job.client_id:
        raise ForbiddenError(
            "Only the job's client can accept or reject work.", code="client_only"
        )
    if defect.status != DefectStatus.RECTIFIED:
        raise ConflictError(
            "Work must be marked Rectified before a decision.", code="not_rectified"
        )
    if data.decision == RectificationDecision.REJECTED and not data.reason:
        raise AppError("A reason is required when rejecting.", code="reason_required")

    rect.decision = data.decision
    rect.decided_by = client.id
    rect.reason = data.reason

    target = (
        DefectStatus.ACCEPTED
        if data.decision == RectificationDecision.ACCEPTED
        else DefectStatus.REJECTED
    )
    await _transition(db, client, defect, target, data.reason)

    # Accept -> notify ID; Reject -> notify ID + contractor.
    recipients = [job.created_by]
    if data.decision == RectificationDecision.REJECTED and defect.assigned_contractor_id:
        recipients.append(defect.assigned_contractor_id)
    await notify(
        db, recipients, type="rectification.decision",
        title=f"Client {data.decision.value.lower()} the rectification: {defect.title}",
        body=data.reason, deep_link=f"/defects/{defect.id}",
    )
    await db.commit()
    await db.refresh(rect)
    return rect


# --- Site photos (Requirement 7) ---

async def create_photo(
    db: AsyncSession, user: User, job_id: uuid.UUID, data: PhotoCreate
) -> tuple[Photo, str]:
    job = await get_job_or_404(db, job_id)
    await authorize_job_access(db, user, job)

    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if data.size_bytes > max_bytes:
        raise AppError("Photo exceeds the size limit.", code="file_too_large")
    if not data.mime_type.startswith("image/"):
        raise AppError("Only image files are allowed.", code="unsupported_type")

    if data.defect_id:
        defect = await db.get(Defect, data.defect_id)
        if not defect or defect.job_id != job_id:
            raise NotFoundError("Defect not found on this job.", code="defect_not_found")

    storage = get_storage()
    key = storage.generate_key(f"jobs/{job_id}/photos", data.filename)
    photo = Photo(
        job_id=job_id, defect_id=data.defect_id, storage_key=key,
        caption=data.caption, uploaded_by=user.id,
    )
    db.add(photo)
    await write_audit(
        db, actor_id=user.id, action="photo.upload", target_type="photo",
        target_id=str(photo.id), job_id=job_id,
    )
    await db.commit()
    await db.refresh(photo)
    return photo, storage.presigned_put_url(key, data.mime_type)


async def list_photos(db: AsyncSession, user: User, job_id: uuid.UUID) -> list[Photo]:
    job = await get_job_or_404(db, job_id)
    await authorize_job_access(db, user, job)
    rows = await db.scalars(
        select(Photo).where(Photo.job_id == job_id).order_by(Photo.created_at.desc())
    )
    return list(rows.all())


def photo_download_url(photo: Photo) -> str:
    return get_storage().presigned_get_url(photo.storage_key)
