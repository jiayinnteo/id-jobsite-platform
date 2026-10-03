"""FastAPI application entrypoint."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
)

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
    }


@app.get("/", tags=["system"])
async def root() -> dict:
    return {"message": f"{settings.app_name} — see /docs for the API."}
