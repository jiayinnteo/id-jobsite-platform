"""arq worker definitions.

Background jobs run here: AI drafting, WhatsApp send retries, calendar sync, and
push delivery. In local dev these run inline from the services; the worker gives
a place to offload slow/retryable work in production.
"""

from __future__ import annotations

from app.core.config import get_settings

settings = get_settings()


async def ping(ctx) -> str:
    """Health task used to verify the worker is processing jobs."""
    return "pong"


class WorkerSettings:
    """arq entrypoint: `arq app.workers.WorkerSettings`."""

    functions = [ping]
    redis_settings_url = settings.redis_url

    @staticmethod
    async def on_startup(ctx) -> None:
        ctx["settings"] = settings
