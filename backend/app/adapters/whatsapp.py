"""WhatsAppPort — WhatsApp Business Cloud API behind an interface.

Disabled/mock mode runs when credentials are absent so the rest of the app
(in-app chat, bridge wiring) works without a Meta account (Requirement 12.3).
Returns a synthetic external message id used for idempotent bridging.
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

import httpx

from app.core.config import get_settings


class WhatsAppPort(ABC):
    @property
    @abstractmethod
    def enabled(self) -> bool: ...

    @abstractmethod
    async def send_text(self, *, to_number: str, body: str) -> str:
        """Send a text message; return the WhatsApp message id."""


class MockWhatsApp(WhatsAppPort):
    @property
    def enabled(self) -> bool:
        return False

    async def send_text(self, *, to_number: str, body: str) -> str:
        return f"wamid.mock-{uuid.uuid4()}"


class CloudWhatsApp(WhatsAppPort):
    def __init__(self, token: str, phone_number_id: str):
        self._token = token
        self._phone_number_id = phone_number_id

    @property
    def enabled(self) -> bool:
        return True

    async def send_text(self, *, to_number: str, body: str) -> str:
        url = f"https://graph.facebook.com/v20.0/{self._phone_number_id}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "text",
            "text": {"body": body},
        }
        headers = {"Authorization": f"Bearer {self._token}"}
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return data["messages"][0]["id"]


def get_whatsapp() -> WhatsAppPort:
    settings = get_settings()
    if settings.whatsapp_enabled and settings.whatsapp_token and settings.whatsapp_phone_number_id:
        return CloudWhatsApp(settings.whatsapp_token, settings.whatsapp_phone_number_id)
    return MockWhatsApp()
