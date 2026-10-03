"""PushPort — device push notifications behind an interface.

Mock implementation (no-op, records intent) runs when FCM/APNs is not
configured, so notification delivery never breaks the app in dev.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class PushPort(ABC):
    @abstractmethod
    async def send(self, *, device_tokens: list[str], title: str, body: str | None) -> None: ...


class MockPush(PushPort):
    async def send(self, *, device_tokens, title, body) -> None:
        # No-op in dev/test. In production this calls FCM/APNs.
        return None


def get_push() -> PushPort:
    # A real FCM/APNs adapter is selected here once credentials are configured.
    return MockPush()
