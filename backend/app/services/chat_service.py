"""In-app chat with the WhatsApp bridge.

A job has one Conversation spanning both channels. Sending an in-app message
also delivers it to WhatsApp (if enabled and the client has a number). Inbound
WhatsApp messages mirror into the conversation. De-dup is keyed on
(channel, external_id) so a bridged message is never echoed back.
"""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.whatsapp import get_whatsapp
from app.core.errors import NotFoundError
from app.core.ws_manager import manager
from app.models.chat import (
    Channel,
    Conversation,
    Message,
    MessageDirection,
    MessageRead,
)
from app.models.job import Job
from app.models.user import User
from app.schemas.chat import MessageCreate, MessageOut
from app.services.common import (
    authorize_job_access,
    get_job_or_404,
    member_user_ids,
    notify,
    write_audit,
)


async def get_or_create_conversation(db: AsyncSession, job_id: uuid.UUID) -> Conversation:
    convo = await db.scalar(select(Conversation).where(Conversation.job_id == job_id))
    if convo is None:
        convo = Conversation(job_id=job_id)
        db.add(convo)
        await db.flush()
    return convo


async def get_conversation_for_job(
    db: AsyncSession, user: User, job_id: uuid.UUID
) -> Conversation:
    job = await get_job_or_404(db, job_id)
    await authorize_job_access(db, user, job)
    return await get_or_create_conversation(db, job_id)


async def list_messages(
    db: AsyncSession, user: User, conversation_id: uuid.UUID
) -> list[Message]:
    convo = await db.get(Conversation, conversation_id)
    if not convo:
        raise NotFoundError("Conversation not found.", code="conversation_not_found")
    job = await get_job_or_404(db, convo.job_id)
    await authorize_job_access(db, user, job)
    rows = await db.scalars(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    return list(rows.all())


async def _broadcast(message: Message) -> None:
    await manager.broadcast(
        str(message.conversation_id),
        {
            "id": str(message.id),
            "conversation_id": str(message.conversation_id),
            "channel": message.channel.value,
            "direction": message.direction.value,
            "sender_id": str(message.sender_id) if message.sender_id else None,
            "body": message.body,
            "created_at": message.created_at.isoformat()
            if message.created_at
            else None,
        },
    )


async def send_message(
    db: AsyncSession, user: User, conversation_id: uuid.UUID, data: MessageCreate
) -> Message:
    """A member sends an in-app message. Mirrored out to WhatsApp when possible."""
    convo = await db.get(Conversation, conversation_id)
    if not convo:
        raise NotFoundError("Conversation not found.", code="conversation_not_found")
    job = await get_job_or_404(db, convo.job_id)
    await authorize_job_access(db, user, job)

    message = Message(
        conversation_id=conversation_id,
        channel=Channel.IN_APP,
        direction=MessageDirection.OUTBOUND,
        sender_id=user.id,
        body=data.body,
        attachment_ref=data.attachment_ref,
        linked_entity=data.linked_entity,
    )
    db.add(message)
    await db.flush()

    # Bridge to WhatsApp (idempotent record of the outbound WA copy).
    await _bridge_to_whatsapp(db, job, convo, data.body)

    # Notify offline members (online members get it via WebSocket).
    recipients = [uid for uid in await member_user_ids(db, job) if uid != user.id]
    await notify(
        db, recipients, type="chat.message", title="New message", body=data.body,
        deep_link=f"/jobs/{job.id}/chat",
    )
    await write_audit(
        db, actor_id=user.id, action="chat.send", target_type="message",
        target_id=str(message.id), job_id=job.id,
    )
    await db.commit()
    await db.refresh(message)
    await _broadcast(message)
    return message


async def _bridge_to_whatsapp(
    db: AsyncSession, job: Job, convo: Conversation, body: str
) -> None:
    """Deliver an in-app message to the client's WhatsApp, if enabled."""
    wa = get_whatsapp()
    if not wa.enabled or job.client_id is None:
        return
    client = await db.get(User, job.client_id)
    if not client or not client.phone:
        return
    wa_id = await wa.send_text(to_number=client.phone, body=body)
    # Record the mirrored WhatsApp copy (de-dup on channel+external_id).
    exists = await db.scalar(
        select(Message).where(
            Message.channel == Channel.WHATSAPP, Message.external_id == wa_id
        )
    )
    if not exists:
        db.add(
            Message(
                conversation_id=convo.id,
                channel=Channel.WHATSAPP,
                direction=MessageDirection.OUTBOUND,
                sender_id=None,
                body=body,
                external_id=wa_id,
            )
        )


async def ingest_whatsapp_inbound(
    db: AsyncSession, *, job_id: uuid.UUID, from_number: str, body: str, external_id: str
) -> Message | None:
    """Mirror an inbound WhatsApp message into the job conversation (idempotent)."""
    existing = await db.scalar(
        select(Message).where(
            Message.channel == Channel.WHATSAPP, Message.external_id == external_id
        )
    )
    if existing:
        return None  # already ingested

    convo = await get_or_create_conversation(db, job_id)
    sender = await db.scalar(select(User).where(User.phone == from_number))
    message = Message(
        conversation_id=convo.id,
        channel=Channel.WHATSAPP,
        direction=MessageDirection.INBOUND,
        sender_id=sender.id if sender else None,
        body=body,
        external_id=external_id,
    )
    db.add(message)
    job = await get_job_or_404(db, job_id)
    await notify(
        db, await member_user_ids(db, job), type="chat.message",
        title="New WhatsApp message", body=body, deep_link=f"/jobs/{job_id}/chat",
    )
    await db.commit()
    await db.refresh(message)
    await _broadcast(message)
    return message


async def mark_conversation_read(
    db: AsyncSession, user: User, conversation_id: uuid.UUID
) -> None:
    msgs = await db.scalars(
        select(Message.id).where(Message.conversation_id == conversation_id)
    )
    for mid in msgs.all():
        exists = await db.scalar(
            select(MessageRead).where(
                MessageRead.message_id == mid, MessageRead.user_id == user.id
            )
        )
        if not exists:
            db.add(MessageRead(message_id=mid, user_id=user.id))
    await db.commit()


def to_out(m: Message) -> MessageOut:
    return MessageOut.model_validate(m)
