from __future__ import annotations
from fastapi import APIRouter, HTTPException, Query
from app.dependencies.oauth_authentication import get_adapter, tokens
from app.dependencies.utility import maybe_await
from app.models import OrderRequest  # eksisterende model

router = APIRouter(prefix="/trade", tags=["trade"])

@router.post("/buy")
async def trade_buy(symbol: str = Query(...), quantity: int = Query(..., gt=0)):
    try:
        info = await maybe_await(get_adapter().verify_connection(tokens()))
        acc = getattr(info, "default_account_key", None)
        if not acc:
            raise HTTPException(status_code=401, detail="No DefaultAccountKey (not connected?)")
        req = OrderRequest(account_key=acc, symbol=symbol, side="Buy", quantity=quantity)
        out = await maybe_await(get_adapter().place_order(tokens(), req))
        return out
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/sell")
async def trade_sell(symbol: str = Query(...), quantity: int = Query(..., gt=0)):
    try:
        info = await maybe_await(get_adapter().verify_connection(tokens()))
        acc = getattr(info, "default_account_key", None)
        if not acc:
            raise HTTPException(status_code=401, detail="No DefaultAccountKey (not connected?)")
        req = OrderRequest(account_key=acc, symbol=symbol, side="Sell", quantity=quantity)
        out = await maybe_await(get_adapter().place_order(tokens(), req))
        return out
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
