"""Unit tests for the role-based access control dependency factory."""

import types

import pytest

from app.api.deps import require_roles
from app.core.errors import ForbiddenError
from app.models.user import UserRole


def _user(role: UserRole):
    return types.SimpleNamespace(id="u1", role=role)


@pytest.mark.asyncio
async def test_require_roles_allows_matching_role():
    checker = require_roles(UserRole.ID, UserRole.ID_BOSS)
    user = _user(UserRole.ID_BOSS)
    assert await checker(user=user) is user


@pytest.mark.asyncio
async def test_require_roles_blocks_other_roles():
    checker = require_roles(UserRole.ID)
    with pytest.raises(ForbiddenError):
        await checker(user=_user(UserRole.CLIENT))
