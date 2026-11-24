from typing import List
from uuid import UUID
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.db.session import get_session
from apps.api.db.models import CVSuggestion, User
from apps.api.schemas import TailorResultOut
from apps.api.agents.cv_tailor import tailor_cv

router = APIRouter()


@router.post("/tailor", response_model=TailorResultOut)
async def tailor_cv_endpoint(
    file: UploadFile = File(...),
    jd_text: str = "",
    user_id: UUID = None,
    session: AsyncSession = Depends(get_session),
):
    # TODO: extract CV text from PDF/DOCX
    cv_text = ""

    if not user_id:
        raise HTTPException(status_code=400, detail="user_id required")

    result = await tailor_cv(cv_text, jd_text)

    db_suggestion = CVSuggestion(
        user_id=user_id,
        overall_match_score=result.overall_match_score,
        ats_compatibility=result.ats_compatibility,
        suggestions=result.suggestions,
        rewrite_summary=result.rewrite_summary,
    )
    session.add(db_suggestion)
    await session.commit()
    await session.refresh(db_suggestion)
    return db_suggestion