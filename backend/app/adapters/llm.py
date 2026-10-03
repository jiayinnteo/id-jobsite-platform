"""LLMPort — provider-agnostic LLM access behind an interface.

Mock implementation returns a deterministic, natural-sounding draft so the
human-in-the-loop flow works end-to-end without any provider credentials.
Real providers (OpenAI/Anthropic/Bedrock) are selected by config and plug in
behind the same interface without changing callers (Requirement 10.6).
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.core.config import get_settings


class LLMPort(ABC):
    @abstractmethod
    async def draft_reply(self, *, context: str, last_message: str) -> str:
        """Return a natural-language draft reply. Never sends anything."""


class MockLLM(LLMPort):
    async def draft_reply(self, *, context: str, last_message: str) -> str:
        snippet = last_message.strip()
        if len(snippet) > 80:
            snippet = snippet[:77] + "..."
        return (
            "Hi! Thanks for your message. "
            f'Regarding "{snippet}", we\'ve noted it and will update you shortly. '
            "Please let us know if there's anything else we can help with."
        )


class ProviderLLM(LLMPort):
    """Placeholder for a real provider; falls back to mock output until a
    concrete SDK is wired, so the pipeline never breaks."""

    def __init__(self, provider: str, api_key: str | None, model: str | None):
        self._provider = provider
        self._api_key = api_key
        self._model = model
        self._fallback = MockLLM()

    async def draft_reply(self, *, context: str, last_message: str) -> str:
        # TODO: dispatch to the configured provider SDK using self._api_key.
        return await self._fallback.draft_reply(context=context, last_message=last_message)


def get_llm() -> LLMPort:
    settings = get_settings()
    if settings.llm_provider != "mock" and settings.llm_api_key:
        return ProviderLLM(settings.llm_provider, settings.llm_api_key, settings.llm_model)
    return MockLLM()
