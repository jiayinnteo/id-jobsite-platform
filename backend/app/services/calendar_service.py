"""Google Calendar OAuth connect/disconnect and event backfill."""

from __future__ import annotations

from urllib.parse import urlencode

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.errors import AppError, ForbiddenError
from app.models.schedule import CalendarLink
from app.models.user import User

settings = get_settings()

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
SCOPES = "https://www.googleapis.com/auth/calendar.events"


def build_auth_url(state: str) -> str:
    if not settings.google_client_id or not settings.google_redirect_uri:
        raise ForbiddenError("Google Calendar is not configured.", code="google_disabled")
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": SCOPES,
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
    }
    return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"


async def exchange_code(db: AsyncSession, user: User, code: str) -> CalendarLink:
    if not settings.google_client_id or not settings.google_client_secret:
        raise ForbiddenError("Google Calendar is not configured.", code="google_disabled")

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": settings.google_redirect_uri,
                "grant_type": "authorization_code",
            },
        )
    if resp.status_code != 200:
        raise AppError("Failed to connect Google Calendar.", code="google_exchange_failed")
    tokens = resp.json()

    link = await db.scalar(select(CalendarLink).where(CalendarLink.user_id == user.id))
    if not link:
        link = CalendarLink(user_id=user.id)
        db.add(link)
    link.access_token = tokens.get("access_token")
    link.refresh_token = tokens.get("refresh_token") or link.refresh_token
    link.google_calendar_id = "primary"
    link.status = "CONNECTED"
    await db.commit()
    await db.refresh(link)
    return link


async def disconnect(db: AsyncSession, user: User) -> None:
    link = await db.scalar(select(CalendarLink).where(CalendarLink.user_id == user.id))
    if not link:
        return
    token = link.refresh_token or link.access_token
    if token:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                await client.post("https://oauth2.googleapis.com/revoke", data={"token": token})
        except Exception:
            pass
    link.status = "DISCONNECTED"
    link.access_token = None
    link.refresh_token = None
    await db.commit()


async def status_for(db: AsyncSession, user: User) -> dict:
    link = await db.scalar(select(CalendarLink).where(CalendarLink.user_id == user.id))
    connected = bool(link and link.status == "CONNECTED")
    return {"connected": connected, "configured": bool(settings.google_client_id)}
