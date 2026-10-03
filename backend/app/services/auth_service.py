"""Authentication service: registration, login, token refresh."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AuthError, ConflictError
from app.core.security import (
    REFRESH,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import RegisterRequest, TokenPair


async def register_user(db: AsyncSession, data: RegisterRequest) -> User:
    existing = await db.scalar(select(User).where(User.email == data.email.lower()))
    if existing:
        raise ConflictError("An account with this email already exists.", code="email_taken")

    user = User(
        email=data.email.lower(),
        password_hash=hash_password(data.password),
        full_name=data.full_name,
        role=data.role,
        phone=data.phone,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


def _issue_tokens(user: User) -> TokenPair:
    return TokenPair(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
    )


async def login(db: AsyncSession, email: str, password: str) -> TokenPair:
    user = await db.scalar(select(User).where(User.email == email.lower()))
    if not user or not verify_password(password, user.password_hash):
        raise AuthError("Incorrect email or password.", code="invalid_credentials")
    return _issue_tokens(user)


async def refresh_tokens(db: AsyncSession, refresh_token: str) -> TokenPair:
    try:
        payload = decode_token(refresh_token, expected_type=REFRESH)
    except Exception as exc:  # jose.JWTError and friends
        raise AuthError("Invalid or expired refresh token.", code="invalid_token") from exc

    user = await db.get(User, payload["sub"])
    if not user:
        raise AuthError("User no longer exists.", code="invalid_token")
    return _issue_tokens(user)
