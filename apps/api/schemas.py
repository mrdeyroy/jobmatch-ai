from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class JobOut(BaseModel):
    id: UUID
    title: str
    company: str
    location: str
    source: Optional[str] = "manual"
    url: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[List[str]] = None
    match_score: Optional[int] = None
    explanation: Optional[str] = None

    class Config:
        from_attributes = True


class JobSearchRequest(BaseModel):
    query: str
    location: Optional[str] = None
    limit: int = 10
    live: bool = False
    providers: Optional[List[str]] = None


class JobIngestRequest(BaseModel):
    query: Optional[str] = None
    location: Optional[str] = None
    limit: int = 30
    providers: Optional[List[str]] = None


class JobMatchRequest(BaseModel):
    user_id: UUID
    limit: int = 10


class ATSIssue(BaseModel):
    severity: str
    description: str
    fix: str


class ATSReportOut(BaseModel):
    id: UUID
    score: int
    category_scores: Dict[str, int]
    issues: List[ATSIssue]
    matched_keywords: List[str]
    missing_keywords: List[str]

    class Config:
        from_attributes = True


class CVSuggestionItem(BaseModel):
    section: str
    bullet_index: Optional[int] = None
    original: str
    suggested: str
    reason: str
    priority: str
    confidence: float


class TailorResultOut(BaseModel):
    id: UUID
    overall_match_score: int
    ats_compatibility: int
    suggestions: List[CVSuggestionItem]
    rewrite_summary: str

    class Config:
        from_attributes = True


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    conversation_id: Optional[UUID] = None
    message: str


class ChatResponse(BaseModel):
    conversation_id: UUID
    reply: str
    tool_calls: List[Dict[str, Any]] = []


class FeedbackRequest(BaseModel):
    user_id: UUID
    target_type: str
    target_id: UUID
    rating: int
    comment: Optional[str] = ""