from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.db.session import get_session
from apps.api.db.models import Feedback, User
from apps.api.schemas import FeedbackRequest

router = APIRouter()


@router.post("")
async def submit_feedback(
    req: FeedbackRequest,
    session: AsyncSession = Depends(get_session),
):
    # TODO: validate user exists, store rating for eval loop
    feedback = Feedback(
        user_id=req.user_id,
        target_type=req.target_type,
        target_id=req.target_id,
        rating=req.rating,
        comment=req.comment or "",
    )
    session.add(feedback)
    await session.commit()
    return {"status": "recorded"}