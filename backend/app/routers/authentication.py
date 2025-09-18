from __future__ import annotations
from fastapi import APIRouter, HTTPException, Query
from starlette.responses import RedirectResponse
from typing import Optional
from app.dependencies.oauth_authentication import (
    get_oauth, get_adapter, tokens,
    encode_state, decode_state, FRONTEND_ORIGIN
)
from app.dependencies.utility import maybe_await

router = APIRouter(tags=["auth"])

@router.get("/auth/status")
async def auth_status():
    try:
        await maybe_await(get_adapter().verify_connection(tokens()))
        return {"connected": True, "name": None, "fullName": None}
    except Exception:
        return {"connected": False, "name": None, "fullName": None}

@router.get("/auth/login")
async def auth_login(next: Optional[str] = Query(default=None)):
    state = encode_state(next)
    url = get_oauth().build_authorize_url(state=state)
    return RedirectResponse(url, status_code=302)

@router.get("/oauth/callback")
async def oauth_callback(code: str, state: Optional[str] = None):
    try:
        get_oauth().exchange_code(code)
        dest = decode_state(state).get("next", FRONTEND_ORIGIN)
        return RedirectResponse(dest, status_code=302)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me")
async def me():
    try:
        info = await maybe_await(get_adapter().verify_connection(tokens()))
        # Hvis info er Pydantic model
        try:
            return info.model_dump()
        except Exception:
            return info
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
