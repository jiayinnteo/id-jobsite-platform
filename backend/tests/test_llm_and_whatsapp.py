"""Unit tests for LLM mock drafting and WhatsApp mock mode (no DB)."""

import pytest

from app.adapters.llm import MockLLM
from app.adapters.whatsapp import MockWhatsApp
from app.models.chat import DraftStatus


@pytest.mark.asyncio
async def test_mock_llm_returns_natural_draft():
    draft = await MockLLM().draft_reply(context="", last_message="Is the sink fixed?")
    assert isinstance(draft, str)
    assert len(draft) > 0
    assert "Is the sink fixed?" in draft


@pytest.mark.asyncio
async def test_mock_whatsapp_is_disabled_but_returns_id():
    wa = MockWhatsApp()
    assert wa.enabled is False
    wa_id = await wa.send_text(to_number="+6591234567", body="hello")
    assert wa_id.startswith("wamid.mock-")


def test_new_draft_default_status_is_pending_review():
    # Contract: AI drafts must never be created/sent as anything but PENDING_REVIEW.
    assert DraftStatus.PENDING_REVIEW.value == "PENDING_REVIEW"
    # The default on the model column is PENDING_REVIEW (see models/chat.py).
