"""Site-visit scheduling, contractor work queue, and auto Google Calendar linking."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.calendar import CalendarEvent, get_calendar
from app.core.errors import ForbiddenError, NotFoundError
from app.models.defect import Defect, Rectification
from app.models.job import Job
from app.models.schedule import (
    CalendarEventLink,
    CalendarLink,
    SiteVisit,
    VisitStatus,
    VisitWorker,
)
from app.models.user import User, UserRole
from app.schemas.schedule import SiteVisitCreate, SiteVisitUpdate
from app.services.common import (
    authorize_job_access,
    get_job_or_404,
    member_user_ids,
    notify,
    write_audit,
)

ENTITY_SITE_VISIT = "site_visit"


async def _calendar_participants(db: AsyncSession, job: Job, visit: SiteVisit) -> list[uuid.UUID]:
    """Everyone whose calendar should carry this visit."""
    ids = set(await member_user_ids(db, job))
    ids.add(visit.contractor_id)
    for w in visit.workers:
        ids.add(w.worker_id)
    return [i for i in ids if i is not None]


async def _auto_link_calendar(db: AsyncSession, job: Job, visit: SiteVisit) -> None:
    """Create/update a Google Calendar event on each linked participant's calendar.

    Idempotent via CalendarEventLink.google_event_id. Participants who have not
    connected Google are skipped now and backfilled when they connect (R9.2a).
    """
    calendar = get_calendar()
    summary = f"Site visit — {job.name}"
    description = f"Scheduled work at {job.address}"

    for uid in await _calendar_participants(db, job, visit):
        link = await db.scalar(select(CalendarLink).where(CalendarLink.user_id == uid))
        if not link or link.status != "CONNECTED":
            continue  # backfilled on connect

        event_link = await db.scalar(
            select(CalendarEventLink).where(
                CalendarEventLink.entity_type == ENTITY_SITE_VISIT,
                CalendarEventLink.entity_id == visit.id,
                CalendarEventLink.user_id == uid,
            )
        )
        existing = event_link.google_event_id if event_link else None
        event_id = await calendar.upsert_event(
            access_token=link.access_token,
            existing_event_id=existing,
            event=CalendarEvent(
                summary=summary,
                description=description,
                event_date=visit.scheduled_date,
                event_time=visit.scheduled_time,
            ),
        )
        if event_link:
            event_link.google_event_id = event_id
            event_link.last_synced_at = datetime.now(UTC)
        else:
            db.add(
                CalendarEventLink(
                    entity_type=ENTITY_SITE_VISIT,
                    entity_id=visit.id,
                    user_id=uid,
                    google_event_id=event_id,
                    last_synced_at=datetime.now(UTC),
                )
            )


async def create_visit(
    db: AsyncSession, contractor: User, job_id: uuid.UUID, data: SiteVisitCreate
) -> SiteVisit:
    job = await get_job_or_404(db, job_id)
    if contractor.role != UserRole.CONTRACTOR:
        raise ForbiddenError("Only a contractor can schedule a visit.", code="contractor_only")
    await authorize_job_access(db, contractor, job)

    visit = SiteVisit(
        job_id=job_id,
        rectification_id=data.rectification_id,
        contractor_id=contractor.id,
        scheduled_date=data.scheduled_date,
        scheduled_time=data.scheduled_time,
        status=VisitStatus.SCHEDULED,
        created_by=contractor.id,
    )
    db.add(visit)
    await db.flush()
    for wid in data.worker_ids:
        db.add(VisitWorker(site_visit_id=visit.id, worker_id=wid))
    await db.flush()
    await db.refresh(visit, attribute_names=["workers"])

    await _auto_link_calendar(db, job, visit)

    recipients = await member_user_ids(db, job) + list(data.worker_ids)
    await notify(
        db,
        recipients,
        type="visit.scheduled",
        title=f"Site visit scheduled for {data.scheduled_date.isoformat()}",
        body=job.name,
        deep_link=f"/jobs/{job_id}/visits/{visit.id}",
    )
    await write_audit(
        db,
        actor_id=contractor.id,
        action="visit.create",
        target_type="site_visit",
        target_id=str(visit.id),
        job_id=job_id,
    )
    await db.commit()
    await db.refresh(visit, attribute_names=["workers"])
    return visit


async def update_visit(
    db: AsyncSession, user: User, visit_id: uuid.UUID, data: SiteVisitUpdate
) -> SiteVisit:
    visit = await db.get(SiteVisit, visit_id)
    if not visit:
        raise NotFoundError("Site visit not found.", code="visit_not_found")
    job = await get_job_or_404(db, visit.job_id)
    if user.id != visit.contractor_id and user.role not in (UserRole.ID, UserRole.ID_BOSS):
        raise ForbiddenError("You cannot modify this visit.", code="not_owner")
    await authorize_job_access(db, user, job)

    if data.scheduled_date is not None:
        visit.scheduled_date = data.scheduled_date
    if data.scheduled_time is not None:
        visit.scheduled_time = data.scheduled_time
    if data.status is not None:
        visit.status = data.status
    if data.worker_ids is not None:
        for w in list(visit.workers):
            await db.delete(w)
        await db.flush()
        for wid in data.worker_ids:
            db.add(VisitWorker(site_visit_id=visit.id, worker_id=wid))
    await db.flush()
    await db.refresh(visit, attribute_names=["workers"])

    if visit.status == VisitStatus.CANCELLED:
        await _unlink_calendar(db, visit)
    else:
        await _auto_link_calendar(db, job, visit)

    await notify(
        db,
        await member_user_ids(db, job),
        type="visit.updated",
        title="A site visit was updated",
        body=job.name,
        deep_link=f"/jobs/{job.id}/visits/{visit.id}",
    )
    await write_audit(
        db,
        actor_id=user.id,
        action="visit.update",
        target_type="site_visit",
        target_id=str(visit.id),
        job_id=job.id,
        metadata={"status": visit.status.value},
    )
    await db.commit()
    await db.refresh(visit, attribute_names=["workers"])
    return visit


async def _unlink_calendar(db: AsyncSession, visit: SiteVisit) -> None:
    calendar = get_calendar()
    links = await db.scalars(
        select(CalendarEventLink).where(
            CalendarEventLink.entity_type == ENTITY_SITE_VISIT,
            CalendarEventLink.entity_id == visit.id,
        )
    )
    for link in links.all():
        if link.google_event_id:
            cal_link = await db.scalar(
                select(CalendarLink).where(CalendarLink.user_id == link.user_id)
            )
            await calendar.delete_event(
                access_token=cal_link.access_token if cal_link else None,
                event_id=link.google_event_id,
            )
        await db.delete(link)


async def list_visits(db: AsyncSession, user: User, job_id: uuid.UUID) -> list[SiteVisit]:
    job = await get_job_or_404(db, job_id)
    await authorize_job_access(db, user, job)
    rows = await db.scalars(
        select(SiteVisit).where(SiteVisit.job_id == job_id).order_by(SiteVisit.scheduled_date)
    )
    visits = list(rows.all())
    for v in visits:
        await db.refresh(v, attribute_names=["workers"])
    return visits


async def contractor_work_queue(db: AsyncSession, contractor: User) -> list[dict]:
    """All rectification work assigned to this contractor across their jobs."""
    if contractor.role != UserRole.CONTRACTOR:
        raise ForbiddenError("Contractors only.", code="contractor_only")
    rows = await db.execute(
        select(Rectification, Defect)
        .join(Defect, Defect.id == Rectification.defect_id)
        .where(Rectification.contractor_id == contractor.id)
    )
    out = []
    for rect, defect in rows.all():
        out.append(
            {
                "rectification_id": rect.id,
                "defect_id": defect.id,
                "job_id": defect.job_id,
                "defect_title": defect.title,
                "defect_status": defect.status.value,
            }
        )
    return out


async def worker_visits(db: AsyncSession, worker: User) -> list[SiteVisit]:
    """Visits the worker is assigned to."""
    visit_ids = select(VisitWorker.site_visit_id).where(VisitWorker.worker_id == worker.id)
    rows = await db.scalars(
        select(SiteVisit).where(SiteVisit.id.in_(visit_ids)).order_by(SiteVisit.scheduled_date)
    )
    visits = list(rows.all())
    for v in visits:
        await db.refresh(v, attribute_names=["workers"])
    return visits


def visit_to_out_dict(visit: SiteVisit) -> dict:
    return {
        "id": visit.id,
        "job_id": visit.job_id,
        "rectification_id": visit.rectification_id,
        "contractor_id": visit.contractor_id,
        "scheduled_date": visit.scheduled_date,
        "scheduled_time": visit.scheduled_time,
        "status": visit.status,
        "created_at": visit.created_at,
        "worker_ids": [w.worker_id for w in visit.workers],
    }
