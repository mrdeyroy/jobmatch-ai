from typing import List, Dict, Any
import os


async def run_career_agent(message: str):
    """
    Career chat agent with tool stubs and conversation memory.
    Tools: job search, cover-letter writer, résumé analyzer, application tracker.
    Memory: PostgreSQL-backed conversation history.
    TODO: Wire OpenAI function calling + tool execution + memory store/load.
    """
    # Placeholder skeleton
    return (
        "I'm your career agent. I can help you search jobs, tailor your CV, and track applications. "
        "Wire me to OpenAI function calling to enable real tool use.",
        [],
    )