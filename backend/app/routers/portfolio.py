from __future__ import annotations
from fastapi import APIRouter, HTTPException
from typing import List, Any
from app.dependencies.oauth_authentication import get_adapter, tokens
from app.dependencies.utility import maybe_await
from app.utils.normalize_data import as_list_of_dicts, filter_open_orders

router = APIRouter(tags=["portfolio"])

@router.get("/positions")
async def positions():
    try:
        data = await maybe_await(get_adapter().list_positions(tokens()))
        try:
            return [p.model_dump() for p in data]  # hvis p er Pydantic
        except Exception:
            return data
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Position fetch failed: {e}")

@router.get("/orders/open")
async def orders_open():
    try:
        resp = await maybe_await(get_adapter().list_orders(tokens()))
        payload = resp.get("body") if isinstance(resp, dict) and "body" in resp else resp
        items = as_list_of_dicts(payload)
        return filter_open_orders(items)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Orders fetch failed: {e}")
