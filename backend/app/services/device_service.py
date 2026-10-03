"""Device push-token registration and user-targeted push delivery."""

from __future__ import annotations

import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.push import get_push
from app.models.device import DevicePlatform, DeviceToken
from app.models.user import User


async def register_token(
    db: AsyncSession, user: User, *, token: str, platform: DevicePlatform
) -> DeviceToken:
    """Register (or move) a device token to this user. Idempotent per token."""
    existing = await db.scalar(select(DeviceToken).where(DeviceToken.token == token))
    if existing:
        existing.user_id = user.id
        existing.platform = platform
        await db.commit()
        await db.refresh(existing)
        return existing
    row = DeviceToken(user_id=user.id, token=token, platform=platform)
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


async def unregister_token(db: AsyncSession, user: User, token: str) -> None:
    await db.execute(
        delete(DeviceToken).where(
            DeviceToken.token == token, DeviceToken.user_id == user.id
        )
    )
    await db.commit()


async def tokens_for_users(
    db: AsyncSession, user_ids: list[uuid.UUID]
) -> dict[uuid.UUID, list[str]]:
    if not user_ids:
        return {}
    rows = await db.scalars(
        select(DeviceToken).where(DeviceToken.user_id.in_(set(user_ids)))
    )
    out: dict[uuid.UUID, list[str]] = {}
    for row in rows.all():
        out.setdefault(row.user_id, []).append(row.token)
    return out


async def push_to_users(
    db: AsyncSession,
    user_ids: list[uuid.UUID],
    *,
    title: str,
    body: str | None,
    data: dict | None = None,
) -> None:
    """Deliver a push to all of the given users' devices and prune dead tokens."""
    push = get_push()
    if not push.enabled:
        return
    token_map = await tokens_for_users(db, user_ids)
    all_tokens = [t for toks in token_map.values() for t in toks]
    if not all_tokens:
        return
    invalid = await push.send(
        device_tokens=all_tokens, title=title, body=body, data=data
    )
    if invalid:
        await db.execute(delete(DeviceToken).where(DeviceToken.token.in_(invalid)))
        await db.commit()
