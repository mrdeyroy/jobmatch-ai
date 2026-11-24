import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from apps.api.db.session import get_session
from apps.api.db.models import Job, Profile, User
from apps.api.schemas import (
    JobOut,
    JobSearchRequest,
    JobMatchRequest,
    JobIngestRequest,
)
from worker.providers import search_all_providers
from worker.ingest import ingest_live_jobs

router = APIRouter()


@router.post("/search", response_model=List[JobOut])
async def search_jobs(
    req: JobSearchRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Search jobs either across PostgreSQL database (with keyword & location filtering)
    or live across external platforms (Greenhouse, Ashby, Lever, RemoteOK).
    """
    if req.live:
        # Live multi-platform search across ATS platforms and boards
        raw_jobs = await search_all_providers(
            query=req.query,
            location=req.location,
            limit=req.limit,
            providers=req.providers,
        )
        return [
            JobOut(
                id=uuid.uuid5(uuid.NAMESPACE_URL, j.url or f"{j.company}:{j.title}"),
                title=j.title,
                company=j.company,
                location=j.location,
                source=j.source,
                url=j.url,
                description=j.description,
                requirements=j.requirements,
                match_score=None,
                explanation=f"Live listing fetched directly from {j.source.upper()}",
            )
            for j in raw_jobs
        ]

    # Database search
    conditions = [Job.is_active == True]
    if req.query and req.query.strip():
        q = f"%{req.query.strip()}%"
        conditions.append(or_(Job.title.ilike(q), Job.description.ilike(q), Job.company.ilike(q)))

    if req.location and req.location.strip():
        loc_q = f"%{req.location.strip()}%"
        conditions.append(Job.location.ilike(loc_q))

    stmt = select(Job).where(*conditions).limit(req.limit)
    result = await session.execute(stmt)
    jobs = result.scalars().all()

    # Extract URL from description if present
    out_jobs: List[JobOut] = []
    for j in jobs:
        url = None
        desc = j.description or ""
        if desc.startswith("Job URL: "):
            parts = desc.split("\n\n", 1)
            url = parts[0].replace("Job URL: ", "").strip()
            desc = parts[1] if len(parts) > 1 else desc

        out_jobs.append(
            JobOut(
                id=j.id,
                title=j.title,
                company=j.company,
                location=j.location,
                source=j.source,
                url=url,
                description=desc,
                requirements=j.requirements,
                match_score=None,
                explanation=None,
            )
        )
    return out_jobs


@router.post("/ingest")
async def trigger_ingest(
    req: JobIngestRequest,
    background_tasks: BackgroundTasks,
):
    """
    Trigger ingestion of live jobs across platforms into the PostgreSQL database.
    """
    # Run ingestion asynchronously in background or synchronously
    count = await ingest_live_jobs(
        query=req.query,
        location=req.location,
        limit=req.limit,
        providers=req.providers,
    )
    return {"status": "ok", "ingested_count": count}


@router.post("/match", response_model=List[JobOut])
async def match_jobs(
    req: JobMatchRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Ranks active jobs against user profile skills and preferred roles,
    returning match scores and explanations.
    """
    profile_stmt = select(Profile).where(Profile.user_id == req.user_id)
    profile = (await session.execute(profile_stmt)).scalars().first()

    skills = [s.lower() for s in (profile.skills if profile else [])]
    roles = [r.lower() for r in (profile.preferred_roles if profile else [])]

    jobs_result = await session.execute(
        select(Job).where(Job.is_active == True).limit(50)
    )
    all_jobs = jobs_result.scalars().all()

    scored_jobs = []
    for j in all_jobs:
        score = 50  # baseline
        reasons = []

        title_lower = j.title.lower()
        desc_lower = (j.description or "").lower()
        reqs_lower = [r.lower() for r in (j.requirements or [])]

        # Role alignment
        matched_roles = [r for r in roles if r in title_lower]
        if matched_roles:
            score += 25
            reasons.append(f"Matches desired role: {', '.join(matched_roles)}")

        # Skills overlap
        matched_skills = [
            s for s in skills if s in desc_lower or any(s in r for r in reqs_lower)
        ]
        if matched_skills:
            score += min(len(matched_skills) * 10, 25)
            reasons.append(f"Matched skills: {', '.join(matched_skills)}")

        score = min(max(score, 0), 100)
        explanation = "; ".join(reasons) if reasons else "General career match based on profile."

        out_job = JobOut(
            id=j.id,
            title=j.title,
            company=j.company,
            location=j.location,
            source=j.source,
            description=j.description,
            requirements=j.requirements,
            match_score=score,
            explanation=explanation,
        )
        scored_jobs.append(out_job)

    # Sort descending by match_score
    scored_jobs.sort(key=lambda x: x.match_score or 0, reverse=True)
    return scored_jobs[:req.limit]
