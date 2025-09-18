from typing import Literal
from pydantic import BaseModel

class BrokerInfo(BaseModel):
    id: str
    name: str

class AuthStatus(BaseModel):
    connected: bool
    broker: BrokerInfo | None = None
    account_key: str | None = None

class OrderRequest(BaseModel):
    account_key: str
    symbol: str
    side: Literal["Buy", "Sell"]
    quantity: int
    order_type: Literal["Market"] = "Market"

class OrderResponse(BaseModel):
    order_id: str
    status: Literal["Placed", "Rejected", "Prechecked"]

class AccountInfo(BaseModel):
    client_key: str | None = None
    default_account_key: str | None = None

class Position(BaseModel):
    symbol: str
    quantity: float
    avg_price: float