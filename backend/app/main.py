"""FastAPI application entrypoint."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import ai as ai_api
from app.api import auth as auth_api
from app.api import chat as chat_api
from app.api import defects as defects_api
from app.api import documents as documents_api
from app.api import integrations as integrations_api
from app.api import jobs as jobs_api
from app.api import materials as materials_api
from app.api import notifications as notifications_api
from app.api import schedule as schedule_api
from app.api import webhooks as webhooks_api
from app.core.config import get_settings
from app.core.errors import register_error_handlers

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
)

register_error_handlers(app)
_p = settings.api_v1_prefix
app.include_router(auth_api.router, prefix=_p)
app.include_router(jobs_api.router, prefix=_p)
app.include_router(jobs_api.firm_router, prefix=_p)
app.include_router(documents_api.job_docs_router, prefix=_p)
app.include_router(documents_api.docs_router, prefix=_p)
app.include_router(defects_api.job_defects_router, prefix=_p)
app.include_router(defects_api.defects_router, prefix=_p)
app.include_router(defects_api.rect_router, prefix=_p)
app.include_router(schedule_api.job_visits_router, prefix=_p)
app.include_router(schedule_api.visits_router, prefix=_p)
app.include_router(schedule_api.contractor_router, prefix=_p)
app.include_router(schedule_api.worker_router, prefix=_p)
app.include_router(notifications_api.router, prefix=_p)
app.include_router(chat_api.job_chat_router, prefix=_p)
app.include_router(chat_api.chat_router, prefix=_p)
app.include_router(ai_api.router, prefix=_p)
app.include_router(webhooks_api.router, prefix=_p)
app.include_router(integrations_api.router, prefix=_p)
app.include_router(materials_api.suppliers_router, prefix=_p)
app.include_router(materials_api.job_materials_router, prefix=_p)
app.include_router(materials_api.selections_router, prefix=_p)
# WebSocket route (not under the REST prefix).
app.include_router(chat_api.ws_router)

# Mobile app connects from arbitrary origins in dev; tighten in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
async def health() -> dict:
    """Liveness/readiness probe used by orchestration."""
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.environment,
        "storage_mode": settings.storage_mode,
        "whatsapp_enabled": settings.whatsapp_enabled,
        "llm_provider": settings.llm_provider,
        "google_calendar_configured": bool(settings.google_client_id),
    }


@app.get("/", tags=["system"])
async def root() -> dict:
    return {"message": f"{settings.app_name} — see /docs for the API."}
