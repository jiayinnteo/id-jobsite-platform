"""Unit tests for the push adapter (no DB)."""

import pytest

from app.adapters.push import FcmPush, MockPush, get_push


@pytest.mark.asyncio
async def test_mock_push_disabled_and_noop():
    push = MockPush()
    assert push.enabled is False
    invalid = await push.send(device_tokens=["t1", "t2"], title="Hi", body="there")
    assert invalid == []  # nothing invalidated in mock mode


def test_get_push_returns_mock_without_fcm_config():
    # With no FCM_* env configured, we must fall back to the mock adapter.
    assert isinstance(get_push(), MockPush)


def test_fcm_service_account_parses_inline_json():
    push = FcmPush.__new__(FcmPush)  # avoid __init__ (no settings needed)
    sa = push._load_service_account('{"type":"service_account","x":1}')
    assert sa["type"] == "service_account"
    assert push._load_service_account(None) == {}
