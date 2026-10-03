"""Conversation + message endpoints (REST + WebSocket)."""

import uuid

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.ws_manager import manager
from app.db.base import get_db
from app.models.user import User
from app.schemas.chat import ConversationOut, MessageCreate, MessageOut
from app.services import chat_service

job_chat_router = APIRouter(prefix="/jobs", tags=["chat"])
chat_router = APIRouter(prefix="/conversations", tags=["chat"])
ws_router = APIRouter(tags=["chat"])


@job_chat_router.get("/{job_id}/conversation", response_model=ConversationOut)
async def get_conversation(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await chat_service.get_conversation_for_job(db, user, job_id)


@chat_router.get("/{conversation_id}/messages", response_model=list[MessageOut])
async def list_messages(
    conversation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await chat_service.list_messages(db, user, conversation_id)


@chat_router.post("/{conversation_id}/messages", response_model=MessageOut)
async def send_message(
    conversation_id: uuid.UUID,
    data: MessageCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await chat_service.send_message(db, user, conversation_id, data)


@chat_router.post("/{conversation_id}/read")
async def mark_read(
    conversation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await chat_service.mark_conversation_read(db, user, conversation_id)
    return {"status": "ok"}


@ws_router.websocket("/ws/conversations/{conversation_id}")
async def conversation_ws(websocket: WebSocket, conversation_id: str):
    """Realtime delivery. Clients receive broadcast JSON for new messages.
    (Posting is done via the REST endpoint, which authorizes + bridges.)"""
    await manager.connect(conversation_id, websocket)
    try:
        while True:
            # Keep the socket open; ignore client payloads (read-only stream).
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(conversation_id, websocket)
