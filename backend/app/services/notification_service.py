"""Notification queries and read-state."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.models.system import Notification
from app.models.user import User


async def list_notifications(
    db: AsyncSession, user: User, *, only_unread: bool = False
) -> list[Notification]:
    stmt = select(Notification).where(Notification.user_id == user.id)
    if only_unread:
        stmt = stmt.where(Notification.read_at.is_(None))
    stmt = stmt.order_by(Notification.created_at.desc())
    rows = await db.scalars(stmt)
    return list(rows.all())


async def unread_count(db: AsyncSession, user: User) -> int:
    count = await db.scalar(
        select(func.count(Notification.id)).where(
            Notification.user_id == user.id, Notification.read_at.is_(None)
        )
    )
    return count or 0


async def mark_read(db: AsyncSession, user: User, notification_id: uuid.UUID) -> Notification:
    notif = await db.get(Notification, notification_id)
    if not notif or notif.user_id != user.id:
        raise NotFoundError("Notification not found.", code="notification_not_found")
    if notif.read_at is None:
        notif.read_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(notif)
    return notif


async def mark_all_read(db: AsyncSession, user: User) -> int:
    result = await db.execute(
        update(Notification)
        .where(Notification.user_id == user.id, Notification.read_at.is_(None))
        .values(read_at=datetime.now(UTC))
    )
    await db.commit()
    return result.rowcount or 0
