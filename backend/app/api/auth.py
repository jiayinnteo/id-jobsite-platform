"""Authentication endpoints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.base import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    PasswordResetRequest,
    RefreshRequest,
    RegisterRequest,
    TokenPair,
    UserOut,
)
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.register_user(db, data)


@router.post("/login", response_model=TokenPair)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.login(db, data.email, data.password)


@router.post("/refresh", response_model=TokenPair)
async def refresh(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.refresh_tokens(db, data.refresh_token)


@router.post("/password-reset", status_code=status.HTTP_202_ACCEPTED)
async def password_reset(data: PasswordResetRequest, db: AsyncSession = Depends(get_db)):
    # Always 202 so we never reveal whether an email exists. A reset link would
    # be dispatched via the (pluggable) email adapter in a later task.
    return {"message": "If that email exists, a reset link has been sent."}


@router.get("/me", response_model=UserOut)
async def me(user: User = Depends(get_current_user)):
    return user
