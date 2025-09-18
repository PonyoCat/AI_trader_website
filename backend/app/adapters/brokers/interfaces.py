from typing import Protocol, Mapping, Any, Sequence, Literal
from pydantic import BaseModel
from app.models import AccountInfo, Position, OrderRequest, OrderResponse


# Normaliserede modeller som alle adapters kan returnere


class BrokerAdapter(Protocol):
    id: str
    display_name: str

    # Auth check
    def verify_connection(self, tokens: Mapping[str, Any]) -> AccountInfo: ...

    # Portfolio
    def list_positions(self, tokens: Mapping[str, Any]) -> Sequence[Position]: ...

    def list_orders(self, tokens: Mapping[str, Any]) -> Mapping[str, Any]: ...

    # Trading
    def precheck_order(self, tokens: Mapping[str, Any], req: OrderRequest) -> OrderResponse: ...
    
    def place_order(self, tokens: Mapping[str, Any], req: OrderRequest) -> OrderResponse: ...
