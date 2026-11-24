import re
import html
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class RawJobPosting(BaseModel):
    title: str
    company: str
    location: str = "Remote"
    url: str
    description: str = ""
    requirements: List[str] = Field(default_factory=list)
    source: str = "unknown"
    posted_at: Optional[datetime] = None


def clean_html_to_text(content: str, max_chars: int = 5000) -> str:
    """
    Strips script, style, comments, and HTML tags, decoding entities twice safely.
    Inspired by career-ops/providers/_html-to-text.mjs.
    """
    if not content or not isinstance(content, str):
        return ""

    # Remove script and style elements
    text = re.sub(r"<(script|style)\b[^>]*>[\s\S]*?<\/\1\s*>", " ", content, flags=re.IGNORECASE)
    # Remove HTML comments
    text = re.sub(r"<!--[\s\S]*?-->", " ", text)
    # Remove tags
    text = re.sub(r"<(?=[a-z/!?])(?:[^>\"']|\"[^\"]*\"|'[^']*')+>", " ", text, flags=re.IGNORECASE)
    # Decode HTML entities twice
    text = html.unescape(html.unescape(text))
    # Remove any leftover angle brackets
    text = re.sub(r"<[^>]+>", " ", text)
    # Normalize whitespaces
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_chars]


class BaseJobProvider:
    provider_id: str = "base"

    async def fetch_jobs(
        self,
        query: Optional[str] = None,
        location: Optional[str] = None,
        limit: int = 50,
    ) -> List[RawJobPosting]:
        """Fetch jobs matching optional query and location."""
        raise NotImplementedError
