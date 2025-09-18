from __future__ import annotations
from typing import List, Dict, Any, Optional
import os
import httpx
from app.adapters.ai.chat_provider import ChatProvider
from app.adapters.ai.chat_provider_registry import make_http_client, call_with_retry

class GeminiProvider(ChatProvider):
    name = "gemini"

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.base_url = os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta")
        self._client = make_http_client()

    @staticmethod
    def _extract_text(data: Dict[str, Any]) -> str:
        # Forsøg 1: standardsti
        cands = data.get("candidates") or []
        if not cands:
            raise ValueError("Gemini: tomme candidates i svar")
        content = cands[0].get("content") or {}
        parts = content.get("parts") or []
        texts = []
        for p in parts:
            if isinstance(p, dict):
                t = p.get("text")
                if isinstance(t, str) and t:
                    texts.append(t)
        text = "\n".join(texts).strip()
        if text:
            return text
        # Alternativ: nogle svar kan ligge i safetyRatings eller reasoning, håndteres ikke her
        raise ValueError("Gemini: ingen tekst fundet i første kandidat")

    async def chat(
        self,
        messages: List[Dict[str, str]],
        *,
        model: str,
        temperature: float = 0.3,
        max_tokens: int = 2048,
        extra: Optional[Dict[str, Any]] = None
    ) -> str:
        # Konverterer OpenAI-lignende messages -> Gemini "contents"
        contents = []
        for m in messages:
            role = m["role"]
            # Gemini forventer "user" eller "model". System kan lægges som første user-del.
            if role == "system":
                contents.append({"role": "user", "parts": [{"text": m["content"]}]})
            else:
                contents.append({"role": "user" if role == "user" else "model",
                                 "parts": [{"text": m["content"]}]})

        params = {"key": self.api_key}
        url = f"{self.base_url}/models/{model}:generateContent"
        payload: Dict[str, Any] = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }
        if extra:
            payload.update(extra)

        async def _do() -> str:
            r = await self._client.post(url, params=params, json=payload)
            r.raise_for_status()
            data = r.json()
            return self._extract_text(data)

        return await call_with_retry(_do)
