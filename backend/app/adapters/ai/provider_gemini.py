from __future__ import annotations
from typing import Any, Dict, List, Optional
import os

from app.adapters.ai.chat_provider import ChatProvider
from app.adapters.ai.chat_provider_registry import make_http_client, call_with_retry


class GeminiProvider(ChatProvider):
    name = "gemini"

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.base_url = os.getenv(
            "GEMINI_BASE_URL",
            "https://generativelanguage.googleapis.com/v1beta",
        )
        self.default_model = os.getenv(
            "GEMINI_MODEL",
            "models/gemini-1.5-flash-latest",
        )
        self.default_search_model = os.getenv(
            "GEMINI_SEARCH_MODEL",
            self.default_model,
        )
        self._client = make_http_client()

    @staticmethod
    def _extract_text(payload: Dict[str, Any]) -> str:
        """Læser tekst fra første kandidat i Gemini-svaret."""
        candidates = payload.get("candidates") or []
        if not candidates:
            raise ValueError("Gemini: svar indeholder ingen kandidater")

        candidate = candidates[0] if isinstance(candidates[0], dict) else {}
        content = candidate.get("content") if isinstance(candidate, dict) else None
        parts = content.get("parts") if isinstance(content, dict) else None
        texts: List[str] = []
        if isinstance(parts, list):
            for item in parts:
                if isinstance(item, dict):
                    text_part = item.get("text")
                    if isinstance(text_part, str) and text_part.strip():
                        texts.append(text_part.strip())

        if not texts:
            raise ValueError("Gemini: ingen tekst fundet i kandidaten")

        return "\n".join(texts)

    def _build_url(self, model: str) -> str:
        model_path = model if model.startswith("models/") else f"models/{model}"
        return f"{self.base_url}/{model_path}:generateContent"

    async def chat(
        self,
        messages: List[Dict[str, str]],
        *,
        model: str,
        temperature: float = 0.3,
        max_tokens: int = 2048,
        extra: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Sender chat-beskeder til Gemini og returnerer tekstsvaret."""
        contents: List[Dict[str, Any]] = []
        for message in messages:
            role = message.get("role", "user")
            text = message.get("content", "")
            if role == "system":
                contents.append({"role": "user", "parts": [{"text": text}]})
            else:
                contents.append({
                    "role": "user" if role == "user" else "model",
                    "parts": [{"text": text}],
                })

        url = self._build_url(model)
        params = {"key": self.api_key}
        payload: Dict[str, Any] = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }
        if extra:
            payload.update(extra)

        async def _do() -> str:
            response = await self._client.post(url, params=params, json=payload)
            response.raise_for_status()
            data = response.json()
            return self._extract_text(data)

        return await call_with_retry(_do)

    async def web_search(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
        extra: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Bruger Gemini-grounding med Google-søgning til at besvare en prompt."""
        resolved_model = model or self.default_search_model
        url = self._build_url(resolved_model)
        params = {"key": self.api_key}

        payload: Dict[str, Any] = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
            "tools": [{"google_search": {}}],
        }

        extra_payload = (extra or {}).copy()
        include_raw = bool(extra_payload.pop("include_raw_response", False))

        generation_overrides = extra_payload.pop("generationConfig", None)
        if isinstance(generation_overrides, dict):
            payload["generationConfig"].update(generation_overrides)

        tools_override = extra_payload.pop("tools", None)
        if isinstance(tools_override, list):
            payload["tools"] = tools_override

        if extra_payload:
            payload.update(extra_payload)

        async def _do() -> Dict[str, Any]:
            response = await self._client.post(url, params=params, json=payload)
            response.raise_for_status()
            data = response.json()
            text = self._extract_text(data)

            candidates = data.get("candidates") or []
            first_candidate = candidates[0] if candidates and isinstance(candidates[0], dict) else {}

            result: Dict[str, Any] = {
                "text": text,
                "grounding_metadata": first_candidate.get("groundingMetadata"),
            }
            citation_meta = first_candidate.get("citationMetadata") if isinstance(first_candidate, dict) else None
            if citation_meta:
                result["citation_metadata"] = citation_meta
            usage_meta = data.get("usageMetadata")
            if usage_meta:
                result["usage_metadata"] = usage_meta
            if include_raw:
                result["raw"] = data
            return result

        return await call_with_retry(_do)
