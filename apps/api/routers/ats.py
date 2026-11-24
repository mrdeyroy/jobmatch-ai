from typing import List
from uuid import UUID
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.db.session import get_session
from apps.api.db.models import ATSReport, User
from apps.api.schemas import ATSReportOut
from apps.api.agents.ats_agent import analyze_resume

router = APIRouter()


@router.post("/score", response_model=ATSReportOut)
async def score_resume(
    file: UploadFile = File(...),
    user_id: UUID = None,
    session: AsyncSession = Depends(get_session),
):
    # TODO: extract text from PDF/DOCX using pdfplumber / python-docx
    resume_text = ""

    if not user_id:
        raise HTTPException(status_code=400, detail="user_id required")

    report = await analyze_resume(resume_text)

    db_report = ATSReport(
        user_id=user_id,
        score=report.score,
        category_scores=report.category_scores,
        issues=report.issues,
        matched_keywords=report.matched_keywords,
        missing_keywords=report.missing_keywords,
    )
    session.add(db_report)
    await session.commit()
    await session.refresh(db_report)
    return db_report