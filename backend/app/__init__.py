# app/__init__.py
from pathlib import Path
from dotenv import load_dotenv

# find projektroden og læs .env filen
HERE = Path(__file__).resolve()
BACKEND = HERE.parent.parent          # .../backend
ENV_FILE = BACKEND / ".env"           # .../backend/.env

# Load once, override any inherited env so we don't pick up stale values
load_dotenv(ENV_FILE, override=True)