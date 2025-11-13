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

    @staticmethod
    def _extract_response_text(data: Dict[str, Any]) -> str:
        """Finds the first textual chunk in a Responses- eller ChatCompletions-svar."""
        outputs = data.get("output") or data.get("outputs") or []
        for block in outputs:
            if not isinstance(block, dict):
                continue
            contents = block.get("content") or []
            for item in contents:
                if not isinstance(item, dict):
                    continue
                if item.get("type") in {"output_text", "text"}:
                    text_val = item.get("text")
                    if isinstance(text_val, str) and text_val.strip():
                        return text_val.strip()
        choices = data.get("choices") or []
        for choice in choices:
            if not isinstance(choice, dict):
                continue
            message = choice.get("message") or {}
            if isinstance(message, dict):
                content = message.get("content")
                if isinstance(content, str) and content.strip():
                    return content.strip()
                if isinstance(content, list):
                    for part in content:
                        if not isinstance(part, dict):
                            continue
                        if part.get("type") == "text":
                            part_text = part.get("text")
                            if isinstance(part_text, str) and part_text.strip():
                                return part_text.strip()
        raise ValueError("OpenAI: ingen tekst fundet i svar")

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

    async def web_search(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
        extra: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Executes a Responses API call med web-søgeværktøjet slået til."""
        url = f"{self.base_url}/responses"
        resolved_model = model or os.getenv("OPENAI_SEARCH_MODEL", "gpt-4.1-mini")
        payload: Dict[str, Any] = {
            "model": resolved_model,
            "input": prompt,
            "temperature": temperature,
            "max_output_tokens": max_tokens,
            "tools": [{"type": "web_search"}],
        }

        extra_payload = (extra or {}).copy()
        include_raw = bool(extra_payload.pop("include_raw_response", False))

        tools_override = extra_payload.pop("tools", None)
        if tools_override:
            payload["tools"] = tools_override

        if "max_output_tokens" in extra_payload:
            payload["max_output_tokens"] = extra_payload.pop("max_output_tokens")
        if "temperature" in extra_payload:
            payload["temperature"] = extra_payload.pop("temperature")
        if "input" in extra_payload:
            payload["input"] = extra_payload.pop("input")
        if "messages" in extra_payload:
            # Responses API accepterer "messages" som alternativ til "input".
            payload["messages"] = extra_payload.pop("messages")
            payload.pop("input", None)

        if extra_payload:
            payload.update(extra_payload)

        async def _do() -> Dict[str, Any]:
            r = await self._client.post(
                url,
                json=payload,
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            r.raise_for_status()
            data = r.json()
            text = self._extract_response_text(data)

            results: List[Dict[str, Any]] = []
            top_level_results = data.get("web_search_results")
            if isinstance(top_level_results, list):
                results.extend([res for res in top_level_results if isinstance(res, dict)])

            outputs = data.get("output") or data.get("outputs") or []
            for block in outputs:
                if not isinstance(block, dict):
                    continue
                contents = block.get("content") or []
                for item in contents:
                    if not isinstance(item, dict):
                        continue
                    if item.get("type") in {"web_search_results", "tool_output"}:
                        payload_results = item.get("results") or item.get("output")
                        if isinstance(payload_results, list):
                            results.extend([res for res in payload_results if isinstance(res, dict)])

            response: Dict[str, Any] = {
                "text": text,
                "web_results": results or None,
                "usage": data.get("usage"),
            }
            if include_raw:
                response["raw"] = data
            return response

        return await call_with_retry(_do)
