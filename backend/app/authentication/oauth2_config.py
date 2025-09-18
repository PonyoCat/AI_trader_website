from dataclasses import dataclass, field
from typing import Optional, Dict, Callable
import os

@dataclass  # En klasse uden funktioner som kun er data
class OAuth2Config:  # Klasse der indeholder alt vi skal bruge for OAuth2
    name: str
    authorize_url: str
    token_url: str
    client_id: str
    client_secret: str
    redirect_uri: str
    scope: Optional[str] = None
    extra_auth_params: Dict[str, str] = field(default_factory=dict)
    extra_token_params: Dict[str, str] = field(default_factory=dict)

def _env(prefix: str, key: str) -> str:
    """Henter påkrævet env-variabel som f.eks. SAXO_AUTH_URL; fejler tydeligt hvis den mangler."""
    value = os.getenv(f"{prefix}_{key}")
    if not value:
        raise KeyError(f"Missing env {prefix}_{key}")
    return value

def load_oauth2_from_env(prefix: str, name: str) -> OAuth2Config:
    """
    Læs OAuth2 konfiguration fra env.
    Hvis {PREFIX}_AUTHORIZE_URL / {PREFIX}_TOKEN_URL er sat, bruges de direkte.
    Ellers bygges de som {PREFIX}_AUTH_URL + '/authorize' og '/token'.
    """
    # Tillad enten fulde endpoints ELLER base-URL
    auth_base = os.getenv(f"{prefix}_AUTH_URL")  # valgfri hvis AUTHORIZE/TOKEN er sat
    authorize_url = os.getenv(f"{prefix}_AUTHORIZE_URL")
    token_url     = os.getenv(f"{prefix}_TOKEN_URL")

    if not (authorize_url and token_url):
        # Fald tilbage til AUTH_URL + suffixer
        if not auth_base:
            raise KeyError(
                f"Missing envs: either set {prefix}_AUTH_URL or both "
                f"{prefix}_AUTHORIZE_URL and {prefix}_TOKEN_URL"
            )
        auth_base = auth_base.rstrip("/")
        authorize_url = authorize_url or f"{auth_base}/authorize"
        token_url     = token_url     or f"{auth_base}/token"

    return OAuth2Config(
        name=name,
        authorize_url=authorize_url,
        token_url=token_url,
        client_id=_env(prefix, "APP_KEY"),
        client_secret=_env(prefix, "APP_SECRET"),
        redirect_uri=_env(prefix, "APP_URL"),
        scope=os.getenv(f"{prefix}_SCOPE") or None,
    )

def make_config(broker: str) -> OAuth2Config:
    """Broker-agnostisk factory. Udvid registry når en ny broker tilføjes."""
    broker = broker.lower()
    registry: Dict[str, Callable[[], OAuth2Config]] = {
        "saxo": lambda: load_oauth2_from_env("SAXO", "saxo"),
        # "ig":   lambda: load_oauth2_from_env("IG",   "ig"),
    }

    # Brug .get så KeyError fra miljø-variabler ikke bliver forvekslet som 'ukendt broker'
    factory = registry.get(broker)
    if not factory:
        available = ", ".join(registry.keys()) or "(none)"
        raise ValueError(f"Unknown broker '{broker}'. Available: {available}")

    return factory()
