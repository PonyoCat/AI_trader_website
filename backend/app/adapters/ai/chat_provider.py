from __future__ import annotations
from typing import Protocol, List, Dict, Any, Optional

class ChatProvider(Protocol):
    name: str

    async def chat(
        self,
        messages: List[Dict[str, str]],
        *,
        model: str,
        temperature: float = 0.3,
        max_tokens: int = 2048,
        extra: Optional[Dict[str, Any]] = None
    ) -> str: ...
