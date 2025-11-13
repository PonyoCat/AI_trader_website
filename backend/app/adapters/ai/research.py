from __future__ import annotations
from typing import Dict, Any, List, Optional
from pathlib import Path
import json
import os

from app.adapters.ai.chat_provider_registry import ProviderRegistry
from app.adapters.ai.chat_provider import ChatProvider
from app.adapters.ai.provider_openai import OpenAIProvider  # antag filnavn

REPO_ROOT = Path(__file__).resolve().parents[2]
PROMPTS_DIR = REPO_ROOT / "shared" / "prompts" / "ai_trader"

def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()

def _build_find_system() -> str:
    base = _read(PROMPTS_DIR / "find_nye_aktier.yaml")
    overlay = (
        "\n\nAdditional requirement:\n"
        "- Return only valid JSON under key 'items' as an array of objects.\n"
        "- Each object must include: id, date, summary, verdict, priority, ticker.\n"
        "- Add a 'ticker' field with the uppercase stock symbol for each item.\n"
        "- Target 15 to 30 items.\n"
    )
    return base + overlay

def _build_deep_system() -> str:
    return _read(PROMPTS_DIR / "undersoeg_aktier_dybt.yaml")

def _extract_ticker_from_id(s: str) -> Optional[str]:
    # Simpel heuristik: før første underscore
    if not s:
        return None
    t = s.split("_", 1)[0].upper()
    return t if t.isalnum() else None

def _normalize_find(raw: Any) -> List[Dict[str, Any]]:
    rows = raw
    if isinstance(raw, dict):
        rows = raw.get("items") or raw.get("results") or []
    items: List[Dict[str, Any]] = []
    for r in rows:
        if not isinstance(r, dict):
            continue
        _id = str(r.get("id", "")).strip()
        ticker = (r.get("ticker") or _extract_ticker_from_id(_id) or "").upper()
        item = {
            "id": _id,
            "date": str(r.get("date", "")),
            "summary": str(r.get("summary", "")),
            "verdict": str(r.get("verdict", "")),
            "priority": int(r.get("priority", 999)),
            "ticker": ticker,
        }
        if item["ticker"]:
            items.append(item)
    items = sorted(items, key=lambda x: x["priority"])[:30]
    return items

def _normalize_deep(raw: Dict[str, Any], wanted_ticker: str) -> Optional[Dict[str, Any]]:
    rid = raw.get("id", "")
    rdate = raw.get("date", "")
    reviews = raw.get("review") or []
    best: Optional[Dict[str, Any]] = None
    for r in reviews:
        t = str(r.get("ticker", "")).upper()
        if not best or t == wanted_ticker:
            best = {
                "id": rid,
                "date": rdate,
                "ticker": t or wanted_ticker,
                "company_name": r.get("company_name"),
                "thesis": r.get("thesis"),
                "catalysts": r.get("catalysts") or [],
                "risks": r.get("risks") or [],
                "red_flags": r.get("red_flags") or [],
                "plan": r.get("plan") or {},
                "verdict": r.get("verdict"),
                "confidence": r.get("confidence"),
                "citations": r.get("citations") or [],
            }
            if t == wanted_ticker:
                break
    return best

async def _call_json(provider: ChatProvider, system: str, user_obj: Dict[str, Any], *, model: str, use_responses: bool = False) -> Any:
    """
    Kald provider og få JSON tilbage. 
    use_responses=True bruger Responses endepunkt via provider.web_search, ellers chat().
    """
    if use_responses:
        # Responses: send hele prompten i 'messages' så værktøjer kan bruges
        extra = {
            "include_raw_response": False,
            "messages": [
                {"role": "system", "content": "Return only valid JSON. No markdown, no comments."},
                {"role": "system", "content": system},
                {"role": "user", "content": json.dumps(user_obj)},
            ],
            "tools": [{"type": "web_search"}],
            "temperature": 0.2,
            "max_output_tokens": 2048,
        }
        res = await provider.web_search(prompt="", model=model, extra=extra)
        return json.loads(res["text"])
    else:
        messages = [
            {"role": "system", "content": "Return only valid JSON. No markdown, no comments."},
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(user_obj)},
        ]
        txt = await provider.chat(messages, model=model, temperature=0.2, max_tokens=2048)
        return json.loads(txt)

async def run_research_loop(
    provider: ChatProvider,
    *,
    today: str,
    universe_hint: Optional[str] = None,
    find_model: str = None,
    deep_model: str = None,
    max_names: int = 30
) -> Dict[str, Any]:
    """
    1) YAML 1: find 15–30 tickers med web søgning
    2) YAML 3: deep research for hver ticker
    """
    find_model = find_model or os.getenv("OPENAI_SEARCH_MODEL", "gpt-4.1-mini")
    deep_model = deep_model or os.getenv("OPENAI_DEEP_MODEL", "gpt-5-thinking")

    # 1) Find nye aktier
    find_system = _build_find_system()
    find_input = {
        "id": f"find_{today}",
        "prompt": universe_hint or "Find attractive micro-cap stocks for this week with verifiable catalysts."
    }
    find_raw = await _call_json(provider, find_system, find_input, model=find_model, use_responses=True)
    found = _normalize_find(find_raw)
    if max_names:
        found = found[:max_names]

    # 2) Dybreviews per ticker
    deep_system = _build_deep_system()
    deep_reviews: List[Dict[str, Any]] = []
    for item in found:
        deep_input = {
            "id": item["id"],
            "date": today,
            "prompt": f"Research deeply the ticker {item['ticker']} and return JSON as specified."
        }
        deep_raw = await _call_json(provider, deep_system, deep_input, model=deep_model, use_responses=True)
        deep = _normalize_deep(deep_raw, item["ticker"])
        if deep:
            deep_reviews.append(deep)

    return {
        "as_of": today,
        "found_count": len(found),
        "found": found,
        "deep_count": len(deep_reviews),
        "deep_reviews": deep_reviews
    }
