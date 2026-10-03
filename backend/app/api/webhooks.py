"""WhatsApp Business Cloud API webhook (verification + inbound receive)."""

from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.base import get_db
from app.models.job import Job
from app.models.user import User
from app.services import chat_service

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
settings = get_settings()


@router.get("/whatsapp")
async def verify(request: Request):
    """Meta sends a GET challenge to verify the webhook."""
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")
    if mode == "subscribe" and token and token == settings.whatsapp_verify_token:
        return Response(content=challenge or "", media_type="text/plain")
    return Response(status_code=status.HTTP_403_FORBIDDEN)


@router.post("/whatsapp")
async def receive(request: Request, db: AsyncSession = Depends(get_db)):
    """Inbound messages are mirrored into the matching job conversation."""
    payload = await request.json()
    try:
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                for msg in value.get("messages", []):
                    from_number = msg.get("from")
                    external_id = msg.get("id")
                    body = (msg.get("text") or {}).get("body", "")
                    if not from_number or not external_id:
                        continue
                    job_id = await _resolve_job(db, from_number)
                    if job_id is None:
                        continue
                    await chat_service.ingest_whatsapp_inbound(
                        db,
                        job_id=job_id,
                        from_number=from_number,
                        body=body,
                        external_id=external_id,
                    )
    except Exception:
        # Always 200 so Meta does not disable the webhook; failures are retried
        # on the next delivery. (Idempotent ingest makes replays safe.)
        pass
    return {"status": "received"}


async def _resolve_job(db: AsyncSession, from_number: str):
    """Find the active job where this phone number is the client."""
    user = await db.scalar(select(User).where(User.phone == from_number))
    if not user:
        return None
    job = await db.scalar(
        select(Job).where(Job.client_id == user.id).order_by(Job.created_at.desc())
    )
    return job.id if job else None
