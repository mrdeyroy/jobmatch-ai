from typing import List, Dict, Any
from pydantic import BaseModel, Field
import os


class ATSReport(BaseModel):
    score: int = Field(ge=0, le=100)
    category_scores: Dict[str, int]
    issues: List[Dict[str, Any]]
    matched_keywords: List[str]
    missing_keywords: List[str]
    rewrite_suggestions: List[str]


async def analyze_resume(resume_text: str, jd_text: str | None = None) -> ATSReport:
    """
    ATS-friendliness agent.
    TODO: Wire OpenAI call with response_format=ATSReport (structured output).
    Tools used upstream: PDF/DOCX parser (pdfplumber/python-docx), section splitter.
    """
    # Placeholder skeleton — replace with real LLM call once OPENAI_API_KEY is set
    return ATSReport(
        score=0,
        category_scores={"formatting": 0, "section_headers": 0, "keyword_match": 0, "readability": 0},
        issues=[],
        matched_keywords=[],
        missing_keywords=[],
        rewrite_suggestions=[],
    )