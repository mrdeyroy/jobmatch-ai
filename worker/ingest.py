"""
Ingest real job postings from multiple platforms (Greenhouse, Ashby, Lever, RemoteOK)
and insert cleaned, validated records into the PostgreSQL jobs table.
"""
import argparse
import asyncio
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from apps.api.db.session import async_session
from apps.api.db.models import Job
from worker.providers import search_all_providers, check_job_liveness


async def ingest_live_jobs(
    query: Optional[str] = None,
    location: Optional[str] = None,
    limit: int = 30,
    providers: Optional[List[str]] = None,
    verify_liveness: bool = False,
) -> int:
    """
    Fetches postings across platforms, deduplicates against DB, and saves them.
    Returns the number of new jobs saved.
    """
    print(f"Fetching jobs from platforms (query='{query}', location='{location}', limit={limit})...")
    raw_jobs = await search_all_providers(
        query=query,
        location=location,
        limit=limit,
        providers=providers,
    )
    print(f"Found {len(raw_jobs)} unique candidates across platforms.")

    saved_count = 0
    async with async_session() as session:
        for rj in raw_jobs:
            # Check if job already exists in DB by title and company
            stmt = select(Job).where(
                Job.title == rj.title,
                Job.company == rj.company,
            )
            existing = (await session.execute(stmt)).scalars().first()
            if existing:
                continue

            if verify_liveness and rj.url:
                is_live = await check_job_liveness(rj.url)
                if not is_live:
                    print(f"Skipping expired/inaccessible job: {rj.title} at {rj.company}")
                    continue

            # Store the job URL in the description header if needed
            full_description = rj.description
            if rj.url and rj.url not in full_description:
                full_description = f"Job URL: {rj.url}\n\n{full_description}"

            posted_date = rj.posted_at or datetime.utcnow()
            if posted_date.tzinfo is not None:
                posted_date = posted_date.replace(tzinfo=None)

            job = Job(
                id=uuid.uuid4(),
                title=rj.title[:255],
                company=rj.company[:255],
                location=rj.location[:255] if rj.location else "Remote",
                description=full_description,
                requirements=rj.requirements,
                source=rj.source[:100],
                posted_at=posted_date,
                is_active=True,
            )
            session.add(job)
            saved_count += 1

        if saved_count > 0:
            await session.commit()

    print(f"Successfully ingested {saved_count} new jobs into database.")
    return saved_count


async def seed():
    """Seed demo/live jobs for quickstart."""
    return await ingest_live_jobs(query="developer", limit=10)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest jobs from ATS and job boards")
    parser.add_argument("--query", "-q", type=str, default=None, help="Job title/keyword filter")
    parser.add_argument("--location", "-l", type=str, default=None, help="Location filter")
    parser.add_argument("--limit", "-n", type=int, default=20, help="Maximum jobs to ingest")
    parser.add_argument("--providers", "-p", nargs="+", default=None, help="Specific providers to run")
    parser.add_argument("--verify-liveness", action="store_true", help="Perform HTTP liveness check")
    args = parser.parse_args()

    asyncio.run(
        ingest_live_jobs(
            query=args.query,
            location=args.location,
            limit=args.limit,
            providers=args.providers,
            verify_liveness=args.verify_liveness,
        )
    )
