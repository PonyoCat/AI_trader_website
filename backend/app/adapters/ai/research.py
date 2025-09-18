from __future__ import annotations
from typing import List, Dict, Any, Optional
import datetime as dt

from app.adapters.ai.chat_provider_registry import ProviderRegistry

SYSTEM_RESEARCH_PROMPT = (
    "Du er en aktieanalytiker med fokus på small og micro cap. "
    "Producerer nøgterne, kildekritiske noter. "
    "Hvis viden er usikker, markeres det tydeligt."
)

def _msg(role: str, content: str) -> Dict[str, str]:
    return {"role": role, "content": content}

class DeepResearchEngine:
    def __init__(self, registry: ProviderRegistry, default_provider: str, default_model: str) -> None:
        self.registry = registry
        self.default_provider = default_provider
        self.default_model = default_model

    async def _call(self, messages: List[Dict[str, str]], *, provider: Optional[str] = None, model: Optional[str] = None, temperature: float = 0.2, max_tokens: int = 2500) -> str:
        p = self.registry.get(provider or self.default_provider)
        return await p.chat(messages, model=model or self.default_model, temperature=temperature, max_tokens=max_tokens)

    async def plan(self, ticker: str, hypothesis: Optional[str] = None) -> Dict[str, Any]:
        prompt = f"""
Udarbejd en kort forskningsplan for {ticker}. Fokus: small eller micro cap.
Lever i JSON:
{{
  "key_questions": ["..."],
  "data_to_collect": ["..."],
  "red_flags": ["..."],
  "valuation_checks": ["..."],
  "initial_hypothesis": "{hypothesis or 'ukendt'}"
}}
Kun JSON.
"""
        out = await self._call([_msg("system", SYSTEM_RESEARCH_PROMPT), _msg("user", prompt)])
        # Simpelt parse; antaget gyldigt JSON fra modellen
        import json
        return json.loads(out)

    async def propose_queries(self, plan: Dict[str, Any], ticker: str) -> List[str]:
        prompt = f"""
Ud fra denne plan og ticker {ticker}, generer 6 web-søgeforespørgsler som strenge i en JSON-liste.
Plan:
{plan}
Kun JSON-listen.
"""
        out = await self._call([_msg("system", SYSTEM_RESEARCH_PROMPT), _msg("user", prompt)])
        import json
        return json.loads(out)

    async def fetch_web_facts(self, queries: List[str]) -> List[Dict[str, Any]]:
        # Placeholder: her kan integreres Bing, SerpAPI, egen scraper m.m.
        # Returnerer tomme facts med "source" og "snippet".
        # Integration kan ske via en ekstern service eller et async modul.
        facts = []
        ts = dt.datetime.utcnow().isoformat() + "Z"
        for q in queries:
            facts.append({"query": q, "source": "web.search.stub", "retrieved_at": ts, "snippet": "Ingen live-søgning aktiveret i denne prototype."})
        return facts

    async def summarise_and_score(self, ticker: str, facts: List[Dict[str, Any]]) -> Dict[str, Any]:
        prompt = f"""
Opsummer disse fund for {ticker} i JSON med felter:
{{
  "company_overview": "string",
  "catalysts": ["..."],
  "risks": ["..."],
  "quality_score": 0..10,
  "confidence": 0..1,
  "missing_information": ["..."]
}}
Vær kritisk og kortfattet. Kun JSON.
Data:
{facts}
"""
        out = await self._call([_msg("system", SYSTEM_RESEARCH_PROMPT), _msg("user", prompt)])
        import json
        return json.loads(out)

    async def build_report(self, ticker: str, plan: Dict[str, Any], summary: Dict[str, Any]) -> Dict[str, Any]:
        # Kan udvides med valuation-blok, teknisk analyse, sentiment m.m.
        return {
            "ticker": ticker,
            "as_of": dt.datetime.utcnow().isoformat() + "Z",
            "plan": plan,
            "findings": summary,
            "disclaimer": "Ikke investeringsråd. Kun til test og udvikling."
        }

    async def run(self, ticker: str, hypothesis: Optional[str] = None, provider: Optional[str] = None, model: Optional[str] = None) -> Dict[str, Any]:
        plan = await self.plan(ticker, hypothesis)
        queries = await self.propose_queries(plan, ticker)
        facts = await self.fetch_web_facts(queries)
        summary = await self.summarise_and_score(ticker, facts)
        report = await self.build_report(ticker, plan, summary)
        report["provider"] = provider or self.default_provider
        report["model"] = model or self.default_model
        return report

