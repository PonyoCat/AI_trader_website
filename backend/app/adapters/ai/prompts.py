from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Tuple

# Standardplacering: repo_root/shared/prompts/ai_trader
DEFAULT_DIR = Path(__file__).resolve().parents[2] / "shared" / "prompts" / "ai_trader"
PROMPTS_DIR = Path(os.getenv("SHARED_PROMPTS_DIR", DEFAULT_DIR))

# Simpel cache med mtime, så der auto-reloades i dev når filen ændres
_cache: Dict[str, Tuple[float, str]] = {}

def _file_for(name: str) -> Path:
    # name: "portfolio" | "note" | "research"
    return PROMPTS_DIR / f"{name}.prompt.txt"

def get_prompt(name: str, reload: bool = False) -> str:
    p = _file_for(name)
    if not p.exists():
        raise FileNotFoundError(f"Prompt not found: {p}")
    mtime = p.stat().st_mtime
    if not reload and name in _cache and _cache[name][0] == mtime:
        return _cache[name][1]
    text = p.read_text(encoding="utf-8").strip()
    _cache[name] = (mtime, text)
    return text

# Korte alias-funktioner, valgfrit
def portfolio_prompt() -> str: return get_prompt("portfolio")
def note_prompt() -> str: return get_prompt("note")
def research_prompt() -> str: return get_prompt("research")
