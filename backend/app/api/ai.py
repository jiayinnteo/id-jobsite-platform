"""AI draft endpoints (human-in-the-loop)."""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.base import get_db
from app.models.user import User
from app.schemas.ai import AIDraftOut, DraftEdit, DraftGenerateRequest
from app.services import ai_service

router = APIRouter(prefix="/ai/drafts", tags=["ai"])


@router.post("", response_model=AIDraftOut)
async def generate(
    data: DraftGenerateRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await ai_service.generate_draft(db, user, data.conversation_id)


@router.get("", response_model=list[AIDraftOut])
async def list_pending(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await ai_service.list_pending(db, user)


@router.patch("/{draft_id}", response_model=AIDraftOut)
async def edit(
    draft_id: uuid.UUID,
    data: DraftEdit,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await ai_service.edit_draft(db, user, draft_id, data.edited_text)


@router.post("/{draft_id}/approve", response_model=AIDraftOut)
async def approve(
    draft_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await ai_service.approve_draft(db, user, draft_id)


@router.post("/{draft_id}/reject", response_model=AIDraftOut)
async def reject(
    draft_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await ai_service.reject_draft(db, user, draft_id)
