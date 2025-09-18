# app/adapters/ig.py
from typing import Mapping, Any, Sequence
from .interfaces import BrokerAdapter, AccountInfo, Position, OrderRequest, OrderResponse

class IGAdapter:
    id = "ig"
    display_name = "IG"

    def __init__(self, base_url: str, timeout: float = 4.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def verify_connection(self, tokens: Mapping[str, Any]) -> AccountInfo:
        # Kald et let endpoint der kræver auth og returner normaliseret info
        raise NotImplementedError

    def list_positions(self, tokens: Mapping[str, Any]) -> Sequence[Position]:
        raise NotImplementedError

    def precheck_order(self, tokens: Mapping[str, Any], req: OrderRequest) -> OrderResponse:
        raise NotImplementedError

    def place_order(self, tokens: Mapping[str, Any], req: OrderRequest) -> OrderResponse:
        raise NotImplementedError