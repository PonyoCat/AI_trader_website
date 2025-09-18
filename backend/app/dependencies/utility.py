# backend/app/dependencies/util.py
from __future__ import annotations
import inspect
from typing import Any

async def maybe_await(x: Any) -> Any:
    return await x if inspect.isawaitable(x) else x
