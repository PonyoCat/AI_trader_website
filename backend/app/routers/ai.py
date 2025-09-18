from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.models_ai import (
    ChatRequest, ChatResponse,
    ResearchRequest, ResearchResponse,
)
from app.adapters.ai.chat_provider_registry import ProviderRegistry
from app.adapters.ai.openai_provider import OpenAIProvider
from app.adapters.ai.gemini_provider import GeminiProvider
from app.adapters.ai.research import DeepResearchEngine

router = APIRouter(prefix="/ai", tags=["ai"])

# Byg et registry én gang pr. proces
_registry = ProviderRegistry()
_registry.register(OpenAIProvider())
_registry.register(GeminiProvider())

@router.post("/chat", response_model=ChatResponse)
async def ai_chat(req: ChatRequest) -> ChatResponse:
    try:
        p = _registry.get(req.provider)
    except KeyError as e:
        raise HTTPException(status_code=400, detail=str(e))
    out = await p.chat(
        [m.model_dump() for m in req.messages],
        model=req.model,
        temperature=req.temperature,
        max_tokens=req.max_tokens,
        extra=req.extra,
    )
    return ChatResponse(content=out)

@router.post("/research", response_model=ResearchResponse)
async def ai_research(req: ResearchRequest) -> ResearchResponse:
    engine = DeepResearchEngine(
        registry=_registry,
        default_provider=req.provider,
        default_model=req.model,
    )
    report = await engine.run(
        req.ticker,
        hypothesis=req.hypothesis,
        provider=req.provider,
        model=req.model,
    )
    return ResearchResponse(**report)
