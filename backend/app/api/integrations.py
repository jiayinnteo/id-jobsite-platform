"""Google Calendar OAuth integration endpoints."""

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.base import get_db
from app.models.user import User
from app.services import calendar_service

router = APIRouter(prefix="/integrations/google", tags=["integrations"])


@router.get("/status")
async def status(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await calendar_service.status_for(db, user)


@router.post("/connect")
async def connect(user: User = Depends(get_current_user)):
    """Returns the Google consent URL the app opens in a browser."""
    return {"auth_url": calendar_service.build_auth_url(state=str(user.id))}


@router.get("/callback")
async def callback(
    code: str,
    state: str,
    db: AsyncSession = Depends(get_db),
):
    """OAuth redirect target. `state` carries the user id."""
    user = await db.get(User, state)
    if user:
        await calendar_service.exchange_code(db, user, code)
    # Redirect back into the app via a deep link.
    return RedirectResponse(url="idjobsite://calendar/connected")


@router.post("/disconnect")
async def disconnect(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await calendar_service.disconnect(db, user)
    return {"status": "disconnected"}
