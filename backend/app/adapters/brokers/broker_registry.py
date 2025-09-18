from .saxo_adapter import SaxoAdapter   # relative import, korrekt pakke
import os

SAXO_BASE = os.environ["SAXO_BASE_URL"]

REGISTRY = {
    "saxo": SaxoAdapter(base_url=SAXO_BASE),
}