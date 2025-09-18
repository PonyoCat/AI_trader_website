from __future__ import annotations
from typing import Dict, Any, Optional, Callable
import asyncio
import httpx
from typing import TypeVar, Awaitable, Callable, Optional


# Relativ import fra samme mappe
from .chat_provider import ChatProvider

class ProviderRegistry:
    def __init__(self) -> None:
        self._providers: Dict[str, ChatProvider] = {}

    def register(self, provider: ChatProvider) -> None:
        self._providers[provider.name] = provider

    def get(self, name: str) -> ChatProvider:
        try:
            return self._providers[name]
        except KeyError:
            raise KeyError(f"Provider '{name}' ikke registreret")

def make_http_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        timeout=httpx.Timeout(20.0, connect=5.0, read=15.0),
        limits=httpx.Limits(max_keepalive_connections=10, max_connections=20),
        follow_redirects=True,
        headers={"User-Agent": "ai-trader-backend/1.0"}
    )

T = TypeVar("T")

async def call_with_retry( # Prøver at kalde API'er med delayed ventetid ved fejl så vi ikke bliver rate limited.
    fn: Callable[[], Awaitable[T]],
    *,
    retries: int = 3,
    base_delay: float = 0.5
) -> T:
    # Forsøg 1..retries med backoff
    for i in range(retries):
        try:
            return await fn()
        except httpx.HTTPStatusError as e:
            if e.response is not None and e.response.status_code in (429, 500, 502, 503, 504):
                await asyncio.sleep(base_delay * (2 ** i))
                continue
            raise
        except (httpx.ReadTimeout, httpx.ConnectTimeout):
            await asyncio.sleep(base_delay * (2 ** i))
            continue

    # Final attempt uden catch. Returnerer T eller rejser exception.
    return await fn()
