"""Device push-token registration endpoints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.base import get_db
from app.models.user import User
from app.schemas.device import DeviceRegister, DeviceTokenOut, DeviceUnregister
from app.services import device_service

router = APIRouter(prefix="/devices", tags=["devices"])


@router.post("/register", response_model=DeviceTokenOut, status_code=status.HTTP_201_CREATED)
async def register(
    data: DeviceRegister,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await device_service.register_token(db, user, token=data.token, platform=data.platform)


@router.post("/unregister", status_code=status.HTTP_204_NO_CONTENT)
async def unregister(
    data: DeviceUnregister,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await device_service.unregister_token(db, user, data.token)
