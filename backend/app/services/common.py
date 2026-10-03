"""Shared service helpers: audit logging, notifications, job authorization."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ForbiddenError, NotFoundError
from app.models.job import Job, JobMember
from app.models.system import AuditLog, Notification
from app.models.user import User, UserRole


async def write_audit(
    db: AsyncSession,
    *,
    actor_id: uuid.UUID,
    action: str,
    target_type: str,
    target_id: str | None = None,
    job_id: uuid.UUID | None = None,
    metadata: dict | None = None,
) -> None:
    db.add(
        AuditLog(
            actor_id=actor_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            job_id=job_id,
            audit_metadata=metadata,
        )
    )


async def notify(
    db: AsyncSession,
    user_ids: list[uuid.UUID],
    *,
    type: str,
    title: str,
    body: str | None = None,
    deep_link: str | None = None,
) -> None:
    recipients = {u for u in user_ids if u is not None}
    for uid in recipients:
        db.add(
            Notification(
                user_id=uid, type=type, title=title, body=body, deep_link=deep_link
            )
        )
    # Fan out to registered devices too (no-op when FCM is not configured).
    # Imported lazily to avoid a circular import at module load.
    from app.services.device_service import push_to_users

    await push_to_users(
        db,
        list(recipients),
        title=title,
        body=body,
        data={"type": type, "deep_link": deep_link or ""},
    )


async def get_job_or_404(db: AsyncSession, job_id: uuid.UUID) -> Job:
    job = await db.get(Job, job_id)
    if not job:
        raise NotFoundError("Job not found.", code="job_not_found")
    return job


async def is_job_member(db: AsyncSession, job_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    member = await db.scalar(
        select(JobMember).where(
            JobMember.job_id == job_id, JobMember.user_id == user_id
        )
    )
    return member is not None


async def authorize_job_access(db: AsyncSession, user: User, job: Job) -> None:
    """Grant access if the user is the creator, a job member, or an ID_BOSS of
    the owning firm. Raises ForbiddenError otherwise."""
    if user.id == job.created_by or user.id == job.client_id:
        return
    if (
        user.role == UserRole.ID_BOSS
        and job.firm_id is not None
        and user.company_id == job.firm_id
    ):
        return
    if await is_job_member(db, job.id, user.id):
        return
    raise ForbiddenError("You do not have access to this job.", code="not_job_member")


async def member_user_ids(db: AsyncSession, job: Job) -> list[uuid.UUID]:
    rows = await db.scalars(select(JobMember.user_id).where(JobMember.job_id == job.id))
    ids = list(rows.all())
    ids.extend([job.created_by, job.client_id])
    return [i for i in ids if i is not None]
