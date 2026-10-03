"""Jobs, members, boss oversight and client reviews."""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ConflictError, ForbiddenError, NotFoundError
from app.models.job import (
    Job,
    JobMember,
    JobReview,
    JobStatus,
    OversightReview,
)
from app.models.user import User, UserRole
from app.schemas.job import (
    JobCreate,
    JobMemberAdd,
    JobReviewUpsert,
    JobUpdate,
    OversightReviewCreate,
)
from app.services.common import (
    authorize_job_access,
    get_job_or_404,
    notify,
    write_audit,
)


async def create_job(db: AsyncSession, creator: User, data: JobCreate) -> Job:
    job = Job(
        name=data.name,
        address=data.address,
        client_id=data.client_id,
        created_by=creator.id,
        firm_id=creator.company_id,
        status=JobStatus.DRAFT,
    )
    db.add(job)
    await db.flush()
    # Creator is implicitly a member.
    db.add(JobMember(job_id=job.id, user_id=creator.id, role_in_job=creator.role))
    if data.client_id:
        db.add(JobMember(job_id=job.id, user_id=data.client_id, role_in_job=UserRole.CLIENT))
    await write_audit(
        db,
        actor_id=creator.id,
        action="job.create",
        target_type="job",
        target_id=str(job.id),
        job_id=job.id,
    )
    await db.commit()
    await db.refresh(job)
    return job


async def list_jobs_for_user(db: AsyncSession, user: User) -> list[Job]:
    """Jobs the user can see. ID_BOSS sees all jobs in their firm."""
    if user.role == UserRole.ID_BOSS and user.company_id is not None:
        rows = await db.scalars(select(Job).where(Job.firm_id == user.company_id))
        return list(rows.all())

    member_job_ids = select(JobMember.job_id).where(JobMember.user_id == user.id)
    rows = await db.scalars(
        select(Job).where(
            (Job.id.in_(member_job_ids)) | (Job.created_by == user.id) | (Job.client_id == user.id)
        )
    )
    return list(rows.all())


async def get_job(db: AsyncSession, user: User, job_id: uuid.UUID) -> Job:
    job = await get_job_or_404(db, job_id)
    await authorize_job_access(db, user, job)
    return job


async def update_job(db: AsyncSession, user: User, job_id: uuid.UUID, data: JobUpdate) -> Job:
    job = await get_job_or_404(db, job_id)
    if user.role not in (UserRole.ID, UserRole.ID_BOSS):
        raise ForbiddenError("Only the ID firm can update a job.", code="id_only")
    await authorize_job_access(db, user, job)

    if data.name is not None:
        job.name = data.name
    if data.address is not None:
        job.address = data.address
    if data.status is not None:
        job.status = data.status
    await write_audit(
        db,
        actor_id=user.id,
        action="job.update",
        target_type="job",
        target_id=str(job.id),
        job_id=job.id,
        metadata={"status": job.status.value},
    )
    await db.commit()
    await db.refresh(job)
    return job


async def add_member(
    db: AsyncSession, user: User, job_id: uuid.UUID, data: JobMemberAdd
) -> JobMember:
    job = await get_job_or_404(db, job_id)
    if user.role not in (UserRole.ID, UserRole.ID_BOSS):
        raise ForbiddenError("Only the ID firm can manage members.", code="id_only")
    await authorize_job_access(db, user, job)

    exists = await db.scalar(
        select(JobMember).where(JobMember.job_id == job_id, JobMember.user_id == data.user_id)
    )
    if exists:
        raise ConflictError("User is already a member of this job.", code="already_member")

    member = JobMember(job_id=job_id, user_id=data.user_id, role_in_job=data.role_in_job)
    db.add(member)
    if data.role_in_job == UserRole.CLIENT and job.client_id is None:
        job.client_id = data.user_id
    await notify(
        db,
        [data.user_id],
        type="job.added",
        title="You've been added to a job",
        body=job.name,
        deep_link=f"/jobs/{job.id}",
    )
    await write_audit(
        db,
        actor_id=user.id,
        action="job.add_member",
        target_type="job_member",
        target_id=str(data.user_id),
        job_id=job.id,
    )
    await db.commit()
    await db.refresh(member)
    return member


# --- ID_BOSS oversight (Requirement 15) ---


async def add_oversight_review(
    db: AsyncSession, boss: User, job_id: uuid.UUID, data: OversightReviewCreate
) -> OversightReview:
    job = await get_job_or_404(db, job_id)
    if boss.role != UserRole.ID_BOSS or job.firm_id != boss.company_id:
        raise ForbiddenError("Only the firm's boss can add oversight reviews.", code="boss_only")
    review = OversightReview(job_id=job_id, boss_id=boss.id, flag=data.flag, note=data.note)
    db.add(review)
    # Notify the ID who runs the job (internal only).
    await notify(
        db,
        [job.created_by],
        type="oversight.review",
        title=f"Boss review: {data.flag.value.replace('_', ' ').title()}",
        body=data.note,
        deep_link=f"/jobs/{job.id}",
    )
    await write_audit(
        db,
        actor_id=boss.id,
        action="job.oversight_review",
        target_type="job",
        target_id=str(job.id),
        job_id=job.id,
        metadata={"flag": data.flag.value},
    )
    await db.commit()
    await db.refresh(review)
    return review


# --- Client reviews (Requirement 16) ---


async def upsert_job_review(
    db: AsyncSession, client: User, job_id: uuid.UUID, data: JobReviewUpsert
) -> JobReview:
    job = await get_job_or_404(db, job_id)
    if client.id != job.client_id:
        raise ForbiddenError("Only the job's client can review it.", code="client_only")
    if job.status != JobStatus.COMPLETED:
        raise ConflictError("You can only review a completed job.", code="job_not_completed")

    review = await db.scalar(
        select(JobReview).where(JobReview.job_id == job_id, JobReview.client_id == client.id)
    )
    if review:
        review.rating = data.rating
        review.comment = data.comment
        action = "job.review_update"
    else:
        review = JobReview(
            job_id=job_id, client_id=client.id, rating=data.rating, comment=data.comment
        )
        db.add(review)
        action = "job.review_create"

    notify_ids = [job.created_by]
    await notify(
        db,
        notify_ids,
        type="job.reviewed",
        title=f"Client left a {data.rating}★ review",
        body=data.comment,
        deep_link=f"/jobs/{job.id}",
    )
    await write_audit(
        db,
        actor_id=client.id,
        action=action,
        target_type="job",
        target_id=str(job.id),
        job_id=job.id,
        metadata={"rating": data.rating},
    )
    await db.commit()
    await db.refresh(review)
    return review


async def get_job_review(db: AsyncSession, user: User, job_id: uuid.UUID) -> JobReview:
    job = await get_job_or_404(db, job_id)
    await authorize_job_access(db, user, job)
    review = await db.scalar(select(JobReview).where(JobReview.job_id == job_id))
    if not review:
        raise NotFoundError("No review for this job yet.", code="no_review")
    return review


async def firm_average_rating(db: AsyncSession, firm_id: uuid.UUID) -> dict:
    avg = await db.scalar(
        select(func.avg(JobReview.rating))
        .join(Job, Job.id == JobReview.job_id)
        .where(Job.firm_id == firm_id)
    )
    count = await db.scalar(
        select(func.count(JobReview.id))
        .join(Job, Job.id == JobReview.job_id)
        .where(Job.firm_id == firm_id)
    )
    return {"average_rating": round(float(avg), 2) if avg else None, "review_count": count or 0}
