from __future__ import annotations
from typing import Mapping, Any, Sequence, Dict
import requests

# Hvis du har delt interfacet i interfaces.py og models.py, så ret imports:
# from .interfaces import BrokerAdapter
# from .models import AccountInfo, Position, OrderRequest, OrderResponse
from .interfaces import BrokerAdapter, AccountInfo, Position, OrderRequest, OrderResponse


class SaxoAdapter:
    """Adapter til Saxo Bank OpenAPI der implementerer BrokerAdapter interfacet."""

    id = "saxo"
    display_name = "Saxo Bank"

    def __init__(self, base_url: str, timeout: float = 4.0):
        # Saxo base URL bruges til API-kald, fx https://gateway.saxobank.com/sim/openapi
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    # -----------------------------
    # Hjælp: session og instrument
    # -----------------------------
    def _session(self, access_token: str) -> requests.Session:
        """Opretter en requests Session med Bearer token og JSON headers."""
        s = requests.Session()
        s.headers.update({
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        })
        return s

    def _lookup_uic(self, s: requests.Session, symbol: str, asset_types: str = "Stock") -> int:
        """
        Finder UIC for et symbol via reference API.
        Søger på Keywords, matcher eksakt Symbol hvis muligt, ellers tages første.
        """
        params = {
            "Keywords": symbol,
            "AssetTypes": asset_types,
            "IncludeNonTradable": "false",
            "$top": 5,
        }
        r = s.get(f"{self.base_url}/ref/v1/instruments", params=params, timeout=self.timeout)
        r.raise_for_status()
        data = r.json().get("Data", [])
        if not data:
            raise LookupError(f"Instrument ikke fundet for '{symbol}'")
        exact = next((x for x in data if x.get("Symbol") == symbol), None)
        pick = exact or data[0]
        return int(pick["Identifier"])

    # -----------------------------
    # BrokerAdapter: auth check
    # -----------------------------
    def verify_connection(self, tokens: Mapping[str, Any]) -> AccountInfo:
        """
        Tjekker at tokens virker ved at hente kontoliste.
        Returnerer stabil nøgleinfo til UI: ClientKey og DefaultAccountKey.
        """
        access = tokens.get("access_token")
        if not access:
            raise ValueError("No access token")

        s = self._session(access)
        r = s.get(f"{self.base_url}/port/v1/accounts/me", timeout=self.timeout)
        if r.status_code in (401, 403):
            raise ValueError("Unauthorized")
        r.raise_for_status()
        data = r.json()
        first = (data.get("Data") or [None])[0] or {}
        return AccountInfo(
            client_key=first.get("ClientKey"),
            default_account_key=first.get("AccountKey"),
        )

    # -----------------------------
    # BrokerAdapter: portfolio
    # -----------------------------
    def list_positions(self, tokens: Mapping[str, Any]) -> Sequence[Position]:
        """
        Henter åbne positioner og normaliserer til Position modellen.
        Felter er mappet fra Saxos JSON: Amount -> quantity, AverageOpenPrice -> avg_price.
        """
        access = tokens.get("access_token")
        if not access:
            raise ValueError("No access token")

        s = self._session(access)
        r = s.get(f"{self.base_url}/port/v1/positions/me", params={"$top": 100}, timeout=self.timeout)
        r.raise_for_status()
        out: list[Position] = []
        for p in r.json().get("Data", []):
            out.append(
                Position(
                    symbol=p.get("Symbol") or str(p.get("Uic")),
                    quantity=float(p.get("Amount") or 0),
                    avg_price=float(p.get("AverageOpenPrice") or 0),
                )
            )
        return out

    def list_orders(self, tokens: Mapping[str, Any]) -> Dict[str, Any]:
        """Viser åbne ordrer (samme struktur som i dine tidligere helpers)."""
        access = tokens.get("access_token")
        if not access:
            raise ValueError("No access token")
        s = self._session(access)
        r = s.get(f"{self.base_url}/port/v1/orders/me", params={"$top": 50}, timeout=self.timeout)
        try:
            r.raise_for_status()
            return {"ok": True, "status": r.status_code, "body": r.json()}
        except requests.HTTPError:
            body = (r.json() if r.headers.get("Content-Type", "").startswith("application/json") else r.text)
            return {"ok": False, "status": r.status_code, "body": body}

    # -----------------------------
    # BrokerAdapter: trading
    # -----------------------------
    def precheck_order(self, tokens: Mapping[str, Any], req: OrderRequest) -> OrderResponse:
        """
        Tjekker om en ordre kan gennemføres. Succes i precheck garanterer ikke at place også lykkes.
        Payload følger Saxos market order krav.
        """
        access = tokens.get("access_token")
        if not access:
            raise ValueError("No access token")

        s = self._session(access)
        uic = self._lookup_uic(s, req.symbol, asset_types="Stock")
        payload = {
            "AccountKey": req.account_key,
            "Uic": uic,
            "AssetType": "Stock",
            "Amount": int(req.quantity),
            "AmountType": "Quantity",
            "BuySell": req.side,
            "OrderType": req.order_type,  # Market i dit interface
            "ManualOrder": True,
            "OrderDuration": {"DurationType": "DayOrder"},
        }
        r = s.post(f"{self.base_url}/trade/v2/orders/precheck", json=payload, timeout=self.timeout)
        r.raise_for_status()
        data = r.json()
        # Saxo kan returnere forskelligt i precheck. Brug en stabil markør.
        return OrderResponse(order_id=str(data.get("OrderId", "precheck")), status="Prechecked")

    def place_order(self, tokens: Mapping[str, Any], req: OrderRequest) -> OrderResponse:
        """
        Placerer market order. Payload svarer til precheck.
        """
        access = tokens.get("access_token")
        if not access:
            raise ValueError("No access token")

        s = self._session(access)
        uic = self._lookup_uic(s, req.symbol, asset_types="Stock")
        payload = {
            "AccountKey": req.account_key,
            "Uic": uic,
            "AssetType": "Stock",
            "Amount": int(req.quantity),
            "AmountType": "Quantity",
            "BuySell": req.side,
            "OrderType": req.order_type,  # Market i dit interface
            "ManualOrder": True,
            "OrderDuration": {"DurationType": "DayOrder"},
        }
        r = s.post(f"{self.base_url}/trade/v2/orders", json=payload, timeout=self.timeout)
        r.raise_for_status()
        data = r.json()
        return OrderResponse(order_id=str(data.get("OrderId", "")), status="Placed")


