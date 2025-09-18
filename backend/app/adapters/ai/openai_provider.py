from __future__ import annotations
from typing import List, Dict, Any, Optional
import os
import httpx
from app.adapters.ai.chat_provider import ChatProvider
from app.adapters.ai.chat_provider_registry import make_http_client, call_with_retry

class OpenAIProvider(ChatProvider):
    name = "openai"

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self._client = make_http_client()

    async def chat(self, messages: List[Dict[str, str]], *, model: str, temperature: float = 0.3, max_tokens: int = 2048, extra: Optional[Dict[str, Any]] = None) -> str:
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if extra:
            payload.update(extra)

        async def _do():
            r = await self._client.post(
                url,
                json=payload,
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            r.raise_for_status()
            data = r.json()
            # OpenAI-format
            return data["choices"][0]["message"]["content"]

        return await call_with_retry(_do)
