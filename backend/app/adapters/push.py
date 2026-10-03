"""PushPort — device push notifications behind an interface.

Mock implementation (no-op) runs when FCM is not configured, so notification
delivery never breaks the app in dev. The real FCM adapter (HTTP v1) activates
when a Firebase service account + project id are configured.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path

import httpx

from app.core.config import Settings, get_settings


class PushPort(ABC):
    @property
    @abstractmethod
    def enabled(self) -> bool: ...

    @abstractmethod
    async def send(
        self, *, device_tokens: list[str], title: str, body: str | None,
        data: dict | None = None,
    ) -> list[str]:
        """Send to the given tokens; return tokens that are now invalid
        (e.g. unregistered) so the caller can prune them."""


class MockPush(PushPort):
    @property
    def enabled(self) -> bool:
        return False

    async def send(self, *, device_tokens, title, body, data=None) -> list[str]:
        # No-op in dev/test; nothing invalidated.
        return []


class FcmPush(PushPort):
    """Firebase Cloud Messaging HTTP v1 adapter.

    Mints an OAuth2 access token from the service account and posts one message
    per token. Returns tokens FCM reports as UNREGISTERED/invalid for pruning.
    """

    _SCOPE = "https://www.googleapis.com/auth/firebase.messaging"

    def __init__(self, settings: Settings):
        self._project_id = settings.fcm_project_id
        self._sa = self._load_service_account(settings.fcm_service_account)

    @staticmethod
    def _load_service_account(value: str | None) -> dict:
        if not value:
            return {}
        # Accept either a path to the JSON file or the JSON contents directly.
        p = Path(value)
        if p.exists():
            return json.loads(p.read_text())
        return json.loads(value)

    @property
    def enabled(self) -> bool:
        return bool(self._project_id and self._sa)

    async def _access_token(self) -> str:
        # Lazy import so the dependency is only needed when FCM is actually used.
        from google.auth.transport.requests import Request  # type: ignore
        from google.oauth2 import service_account  # type: ignore

        creds = service_account.Credentials.from_service_account_info(
            self._sa, scopes=[self._SCOPE]
        )
        creds.refresh(Request())
        return creds.token

    async def send(self, *, device_tokens, title, body, data=None) -> list[str]:
        if not device_tokens:
            return []
        token = await self._access_token()
        url = f"https://fcm.googleapis.com/v1/projects/{self._project_id}/messages:send"
        headers = {"Authorization": f"Bearer {token}"}
        invalid: list[str] = []
        async with httpx.AsyncClient(timeout=15) as client:
            for device in device_tokens:
                message = {
                    "message": {
                        "token": device,
                        "notification": {"title": title, "body": body or ""},
                        "data": {k: str(v) for k, v in (data or {}).items()},
                    }
                }
                resp = await client.post(url, json=message, headers=headers)
                if resp.status_code == 404 or (
                    resp.status_code == 400 and "UNREGISTERED" in resp.text
                ):
                    invalid.append(device)
        return invalid


def get_push() -> PushPort:
    settings = get_settings()
    if settings.fcm_enabled and settings.fcm_project_id and settings.fcm_service_account:
        return FcmPush(settings)
    return MockPush()
