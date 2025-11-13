from __future__ import annotations
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict, conlist, field_validator

ChatRole = Literal["user", "assistant", "system"]

class ChatMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")
    role: ChatRole
    content: str

class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    provider: str = Field(description="fx openai, gemini, deepseek")
    model: str
    messages: List[ChatMessage]
    temperature: float = 0.3
    max_tokens: int = 2048
    extra: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    content: str

class ResearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ticker: str
    hypothesis: Optional[str] = None
    provider: str = "openai"
    model: str = "gpt-4o-mini"

class ResearchResponse(BaseModel):
    ticker: str
    as_of: str
    provider: str
    model: str
    plan: Dict[str, Any]
    findings: Dict[str, Any]
    disclaimer: str


from pydantic import BaseModel, Field, field_validator
from typing import List

class Source(BaseModel):
    title: str
    url: str

class Finding(BaseModel):
    ticker: str
    company_overview: str
    catalysts: List[str] = Field(default_factory=list)
    risks:     List[str] = Field(default_factory=list)
    quality_score: float = Field(ge=0, le=10)
    confidence: float = Field(ge=0, le=1)
    sources: List[Source] = Field(default_factory=list)

    @field_validator("ticker")
    @classmethod
    def upcase(cls, v: str) -> str:
        return v.upper().strip()
