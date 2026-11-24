from typing import List, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.db.session import get_session
from apps.api.db.models import Conversation, Message, User
from apps.api.schemas import ChatRequest, ChatResponse
from apps.api.agents.career_agent import run_career_agent

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    req: ChatRequest,
    session: AsyncSession = Depends(get_session),
):
    # TODO: load/create conversation, append user message, run agent, save tool calls + memory
    conv_id = req.conversation_id or UUID(int=0)

    reply, tool_calls = await run_career_agent(req.message)

    return ChatResponse(
        conversation_id=conv_id,
        reply=reply,
        tool_calls=tool_calls,
    )