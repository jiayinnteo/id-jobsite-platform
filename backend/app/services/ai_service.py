"""AI draft lifecycle (human-in-the-loop).

Drafts are ALWAYS created in PENDING_REVIEW and never sent automatically.
Approval sends the (optionally edited) text through the chat service, which
also bridges it to WhatsApp. Rejection discards the draft.
"""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.llm import get_llm
from app.core.errors import ConflictError, ForbiddenError, NotFoundError
from app.models.chat import (
    AIDraft,
    Conversation,
    DraftStatus,
    Message,
)
from app.models.user import User, UserRole
from app.schemas.chat import MessageCreate
from app.services import chat_service
from app.services.common import authorize_job_access, get_job_or_404, write_audit


async def _authorize_firm(db: AsyncSession, user: User, conversation_id: uuid.UUID) -> Conversation:
    convo = await db.get(Conversation, conversation_id)
    if not convo:
        raise NotFoundError("Conversation not found.", code="conversation_not_found")
    if user.role not in (UserRole.ID, UserRole.ID_BOSS):
        raise ForbiddenError("Only the ID firm can manage AI drafts.", code="id_only")
    job = await get_job_or_404(db, convo.job_id)
    await authorize_job_access(db, user, job)
    return convo


async def generate_draft(
    db: AsyncSession, user: User, conversation_id: uuid.UUID
) -> AIDraft:
    convo = await _authorize_firm(db, user, conversation_id)

    recent = await db.scalars(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(10)
    )
    messages = list(recent.all())
    last = messages[0].body if messages else ""
    context = "\n".join(m.body for m in reversed(messages))

    draft_text = await get_llm().draft_reply(context=context, last_message=last)

    draft = AIDraft(
        conversation_id=conversation_id,
        message_context=context,
        draft_text=draft_text,
        status=DraftStatus.PENDING_REVIEW,  # NEVER auto-send
    )
    db.add(draft)
    await write_audit(
        db, actor_id=user.id, action="ai.draft_generate", target_type="ai_draft",
        target_id=str(convo.id),
    )
    await db.commit()
    await db.refresh(draft)
    return draft


async def list_pending(db: AsyncSession, user: User) -> list[AIDraft]:
    if user.role not in (UserRole.ID, UserRole.ID_BOSS):
        raise ForbiddenError("Only the ID firm can review AI drafts.", code="id_only")
    rows = await db.scalars(
        select(AIDraft)
        .where(AIDraft.status == DraftStatus.PENDING_REVIEW)
        .order_by(AIDraft.created_at.desc())
    )
    return list(rows.all())


async def edit_draft(
    db: AsyncSession, user: User, draft_id: uuid.UUID, edited_text: str
) -> AIDraft:
    draft = await db.get(AIDraft, draft_id)
    if not draft:
        raise NotFoundError("Draft not found.", code="draft_not_found")
    await _authorize_firm(db, user, draft.conversation_id)
    if draft.status != DraftStatus.PENDING_REVIEW:
        raise ConflictError("Only pending drafts can be edited.", code="not_pending")
    draft.edited_text = edited_text
    await db.commit()
    await db.refresh(draft)
    return draft


async def approve_draft(db: AsyncSession, user: User, draft_id: uuid.UUID) -> AIDraft:
    draft = await db.get(AIDraft, draft_id)
    if not draft:
        raise NotFoundError("Draft not found.", code="draft_not_found")
    await _authorize_firm(db, user, draft.conversation_id)
    if draft.status != DraftStatus.PENDING_REVIEW:
        raise ConflictError("Only pending drafts can be approved.", code="not_pending")

    body = draft.edited_text or draft.draft_text
    # Send via chat service (also bridges to WhatsApp).
    await chat_service.send_message(
        db, user, draft.conversation_id, MessageCreate(body=body)
    )
    draft.status = DraftStatus.SENT
    draft.reviewed_by = user.id
    await write_audit(
        db, actor_id=user.id, action="ai.draft_approve", target_type="ai_draft",
        target_id=str(draft.id),
    )
    await db.commit()
    await db.refresh(draft)
    return draft


async def reject_draft(db: AsyncSession, user: User, draft_id: uuid.UUID) -> AIDraft:
    draft = await db.get(AIDraft, draft_id)
    if not draft:
        raise NotFoundError("Draft not found.", code="draft_not_found")
    await _authorize_firm(db, user, draft.conversation_id)
    if draft.status != DraftStatus.PENDING_REVIEW:
        raise ConflictError("Only pending drafts can be rejected.", code="not_pending")
    draft.status = DraftStatus.REJECTED
    draft.reviewed_by = user.id
    await write_audit(
        db, actor_id=user.id, action="ai.draft_reject", target_type="ai_draft",
        target_id=str(draft.id),
    )
    await db.commit()
    await db.refresh(draft)
    return draft
