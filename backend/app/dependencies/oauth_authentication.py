from __future__ import annotations
import os, json, base64, uuid
from typing import Dict, Any, Optional
from app.authentication.oauth2_config import make_config
from app.authentication.oauth2_client import OAuth2Client
from app.adapters.brokers.saxo_adapter import SaxoAdapter

# Konfiguration
FRONTEND_ORIGIN = os.environ.get("FRONTEND_ORIGIN", "http://127.0.0.1:5173")
SAXO_BASE = os.environ.get("SAXO_BASE_URL", "https://gateway.saxobank.com/sim/openapi").rstrip("/")

# Singletons
_cfg = make_config("saxo")
_oauth = OAuth2Client(_cfg)
_adapter = SaxoAdapter(base_url=SAXO_BASE)

def get_oauth() -> OAuth2Client:
    return _oauth

def get_adapter() -> SaxoAdapter:
    return _adapter

def tokens() -> Dict[str, str]:
    # Adapter-metoder forventer {"access_token": "..."}
    return {"access_token": _oauth.get_access_token()}

def encode_state(next_url: Optional[str]) -> str:
    blob = {"next": next_url or FRONTEND_ORIGIN, "nonce": str(uuid.uuid4())}
    raw = json.dumps(blob).encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")

def decode_state(s: Optional[str]) -> Dict[str, Any]:
    if not s:
        return {}
    pad = "=" * (-len(s) % 4)
    return json.loads(base64.urlsafe_b64decode(s + pad).decode())
