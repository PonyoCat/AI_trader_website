from pathlib import Path
from datetime import datetime, timezone
from .oauth2_config import OAuth2Config
from typing import Dict, Optional
import os, json, uuid, urllib.parse, requests

ROOT = Path(__file__).resolve().parents[2]
SECRETS_DIR = ROOT / ".secrets"
SECRETS_DIR.mkdir(parents=True, exist_ok=True)

def _now() -> int: # Henter bare tid lige nu
    return int(datetime.now(timezone.utc).timestamp())

#-----------------------------------------------------------------
#                                                               --
#  OAuth2 kode for security                                     --
#                                                               --
#-----------------------------------------------------------------

class OAuth2Client:
    config: OAuth2Config
    
    def __init__(self, config: OAuth2Config):
        self.config = config

    def build_authorize_url(self, state: Optional[str] = None) -> str:
        """Din query parameters til en login URL"""
        query_params = {
            "response_type": "code",
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
            "state": state or str(uuid.uuid4()),
            **({"scope": self.config.scope} if self.config.scope else {}),
            **(self.config.extra_auth_params or {}),
        }
        return f"{self.config.authorize_url}?{urllib.parse.urlencode(query_params)}"

    
    
    def get_access_token(self) -> str:
        """Hent en gyldig access token"""
        # 1) Env override: Saxo fx 'SAXO_SIM_ACCESS_TOKEN'
        env_name = f"{self.config.name.upper()}_ACCESS_TOKEN" # hvis name="saxo_sim" forventes env SAXO_SIM_ACCESS_TOKEN.
        if os.getenv(env_name):
            return os.environ[env_name]

        # 2) Leder efter token i lokal fil, hvis den ikke findes så hent tokens først
        tok = self._load()
        if not tok:
            raise RuntimeError("Ingen token fundet. Kør authorize -> exchange først.")

        # 3) Fornyer token hvis man er tættere end 60 sekunder på udløb, kræver dog refresh_token i cahce
        expires_at = tok.get("expires_at")
        if expires_at and _now() >= int(expires_at) - 60:
            rt = tok.get("refresh_token")
            if not rt:
                raise RuntimeError("Token udløbet og ingen refresh_token i cache.")
            tok = self.refresh(rt)
        return tok["access_token"]
    
    @property # @property gør man undgår getter og setter. Man kan også bruge det som om det var et normalt variabel
    def _cache_path(self) -> Path:
        """Hvor tokens gemmes lokalt"""
        return SECRETS_DIR / f"{self.config.name}_token.json"

    def _save(self, payload: dict) -> dict: # Forventer: access_token, evt. refresh_token, evt. expires_in
        """Gemmer tokens i en lokal fil"""
        exp_in = int(payload.get("expires_in", 0)) if payload.get("expires_in") else None 
        data = {
            "access_token": payload["access_token"],
            "refresh_token": payload.get("refresh_token"),
            "expires_at": _now() + exp_in if exp_in else None,
        }
        self._cache_path.write_text(json.dumps(data, indent=2))
        return data

    def _load(self) -> Optional[dict]:
        """Loader tokens fra lokal fil"""
        try:
            if not self._cache_path.exists():
                return None
            return json.loads(self._cache_path.read_text())
        except Exception:
            return None
    
    def refresh(self, refresh_token: str, save: bool = True) -> dict:
        """Bytter refresh token til en ny access token (og evt. ny refresh token)"""
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "redirect_uri": self.config.redirect_uri,
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            **(self.config.extra_token_params or {}),
        }
        r = requests.post(self.config.token_url, data=data, timeout=30)
        r.raise_for_status() # Tjekker for HTTP fejl
        payload = r.json() # 
        return self._save(payload) if save else payload

    def exchange_code(self, code: str, save: bool = True) -> dict:
        """Bytter authorization code til tokens (access_token + refresh_token)"""
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.config.redirect_uri,
            # client_id/secret gives via Basic Auth nu
            **(self.config.extra_token_params or {}),
        }
        return self._post_token(data, save=save)

    def _post_token(self, data: dict, save: bool = True) -> dict: # Token-endpoints forventer form-encoded body og ofte HTTP Basic Client Auth
        """Poster token til broker igennem OAuth2 og henter svar"""
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        r = requests.post(
            self.config.token_url,
            data=data,
            headers=headers,
            auth=(self.config.client_id, self.config.client_secret),  # Basic Auth
            timeout=30,
        )
        try:
            r.raise_for_status()
        except requests.HTTPError:
            # Giv en brugbar fejltekst, inkl. status og serverens body
            raise RuntimeError(f"Token endpoint {r.status_code}: {r.text}")
        payload = r.json()
        return self._save(payload) if save else payload
