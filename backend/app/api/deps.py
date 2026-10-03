"""Shared API dependencies: current user and role-based access control."""

from collections.abc import Iterable

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AuthError, ForbiddenError
from app.core.security import ACCESS, decode_token
from app.db.base import get_db
from app.models.user import User, UserRole

_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    if creds is None:
        raise AuthError("Not authenticated.", code="not_authenticated")
    try:
        payload = decode_token(creds.credentials, expected_type=ACCESS)
    except Exception as exc:
        raise AuthError("Invalid or expired token.", code="invalid_token") from exc

    user = await db.get(User, payload["sub"])
    if not user:
        raise AuthError("User no longer exists.", code="invalid_token")
    return user


def require_roles(*roles: UserRole):
    """Dependency factory enforcing that the current user has one of `roles`."""
    allowed: Iterable[UserRole] = roles

    async def _checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed:
            raise ForbiddenError(
                "You do not have permission to perform this action.",
                code="insufficient_role",
            )
        return user

    return _checker
