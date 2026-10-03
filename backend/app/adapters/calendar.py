"""CalendarPort — Google Calendar behind an interface.

Auto-linking: scheduling services call `upsert_event` for each linked participant.
A Mock implementation runs when Google OAuth is not configured, returning
deterministic event ids so the end-to-end flow works without credentials.
The real Google implementation (OAuth + Calendar API) is wired in Phase 6.
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, time

from app.core.config import get_settings


@dataclass
class CalendarEvent:
    summary: str
    description: str | None
    event_date: date
    event_time: time | None


class CalendarPort(ABC):
    @abstractmethod
    async def upsert_event(
        self,
        *,
        access_token: str | None,
        existing_event_id: str | None,
        event: CalendarEvent,
    ) -> str:
        """Create or update the event; return the Google event id."""

    @abstractmethod
    async def delete_event(self, *, access_token: str | None, event_id: str) -> None: ...


class MockCalendar(CalendarPort):
    async def upsert_event(self, *, access_token, existing_event_id, event) -> str:
        # Keep the same id on update; generate one on create.
        return existing_event_id or f"mock-event-{uuid.uuid4()}"

    async def delete_event(self, *, access_token, event_id) -> None:
        return None


class GoogleCalendar(CalendarPort):
    """Placeholder for the real integration (Phase 6). Falls back to mock
    behavior until the Google client is wired, so nothing breaks."""

    async def upsert_event(self, *, access_token, existing_event_id, event) -> str:
        # TODO(Phase 6): call Google Calendar API with the user's token.
        return existing_event_id or f"google-pending-{uuid.uuid4()}"

    async def delete_event(self, *, access_token, event_id) -> None:
        return None


def get_calendar() -> CalendarPort:
    settings = get_settings()
    if settings.google_client_id and settings.google_client_secret:
        return GoogleCalendar()
    return MockCalendar()
