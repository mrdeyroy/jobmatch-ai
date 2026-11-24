from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import os


class CVSuggestionItem(BaseModel):
    section: str
    bullet_index: Optional[int] = None
    original: str
    suggested: str
    reason: str
    priority: str
    confidence: float


class TailorResult(BaseModel):
    overall_match_score: int = Field(ge=0, le=100)
    ats_compatibility: int = Field(ge=0, le=100)
    suggestions: List[CVSuggestionItem]
    rewrite_summary: str


async def tailor_cv(cv_text: str, jd_text: str) -> TailorResult:
    """
    JD-aware CV tailor agent.
    TODO: Wire OpenAI call with structured output = TailorResult.
    Tools used upstream: JD keyword extractor, CV section parser, truthfulness guardrail
    (no invented companies, titles, or metrics).
    """
    # Placeholder skeleton — replace with real LLM call once OPENAI_API_KEY is set
    return TailorResult(
        overall_match_score=0,
        ats_compatibility=0,
        suggestions=[],
        rewrite_summary="",
    )