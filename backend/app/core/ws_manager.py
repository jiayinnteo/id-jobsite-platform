"""WebSocket connection manager for realtime chat.

Uses an in-process registry for local fan-out. In a multi-instance deployment,
Redis pub/sub bridges instances (publish on send, each instance relays to its
local sockets). The Redis layer is optional in dev; local fan-out always works.
"""

from __future__ import annotations

import asyncio
from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self._rooms: dict[str, set[WebSocket]] = defaultdict(set)
        self._lock = asyncio.Lock()

    async def connect(self, conversation_id: str, ws: WebSocket) -> None:
        await ws.accept()
        async with self._lock:
            self._rooms[conversation_id].add(ws)

    async def disconnect(self, conversation_id: str, ws: WebSocket) -> None:
        async with self._lock:
            self._rooms[conversation_id].discard(ws)
            if not self._rooms[conversation_id]:
                self._rooms.pop(conversation_id, None)

    async def broadcast(self, conversation_id: str, message: dict) -> None:
        async with self._lock:
            targets = list(self._rooms.get(conversation_id, set()))
        for ws in targets:
            try:
                await ws.send_json(message)
            except Exception:
                # Drop broken sockets silently; they'll be cleaned on disconnect.
                pass


manager = ConnectionManager()
