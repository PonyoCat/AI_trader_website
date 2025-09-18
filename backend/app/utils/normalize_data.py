# app/utils/normalize.py
from __future__ import annotations
import json
from typing import Any, Dict, List

def as_list_of_dicts(payload: Any) -> List[Dict[str, Any]]:
    # Saxo svarer typisk {"Data": [...]}
    if isinstance(payload, dict) and "Data" in payload:
        payload = payload["Data"]
    if isinstance(payload, dict):
        payload = [payload]
    if not isinstance(payload, list):
        return []
    out: List[Dict[str, Any]] = []
    for x in payload:
        if hasattr(x, "model_dump"):
            out.append(x.model_dump())
        elif isinstance(x, dict):
            out.append(x)
        elif isinstance(x, str):
            try:
                out.append(json.loads(x))
            except Exception:
                pass
    return out

def filter_open_orders(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    closed = {"filled", "cancelled", "rejected", "expired", "deleted", "done", "executed"}
    out: List[Dict[str, Any]] = []
    for o in items:
        s = str(o.get("Status") or o.get("StatusText") or "").lower()
        if not s or s not in closed:
            out.append(o)
    return out
