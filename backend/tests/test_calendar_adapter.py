"""Unit tests for the mock CalendarPort auto-linking idempotency (no DB)."""

from datetime import date, time

import pytest

from app.adapters.calendar import CalendarEvent, MockCalendar


@pytest.mark.asyncio
async def test_create_then_update_keeps_same_event_id():
    cal = MockCalendar()
    event = CalendarEvent(
        summary="Site visit", description="x", event_date=date(2026, 10, 10),
        event_time=time(9, 0),
    )
    created = await cal.upsert_event(
        access_token="t", existing_event_id=None, event=event
    )
    assert created.startswith("mock-event-")

    # Updating with the same id must return the same id (idempotent).
    updated = await cal.upsert_event(
        access_token="t", existing_event_id=created, event=event
    )
    assert updated == created
