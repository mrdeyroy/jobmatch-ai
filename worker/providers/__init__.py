from typing import List, Dict, Optional
import asyncio

from worker.providers.base import BaseJobProvider, RawJobPosting
from worker.providers.remoteok import RemoteOKProvider
from worker.providers.greenhouse import GreenhouseProvider
from worker.providers.ashby import AshbyProvider
from worker.providers.lever import LeverProvider
from worker.providers.liveness import check_job_liveness

PROVIDERS: Dict[str, BaseJobProvider] = {
    "remoteok": RemoteOKProvider(),
    "greenhouse": GreenhouseProvider(),
    "ashby": AshbyProvider(),
    "lever": LeverProvider(),
}


async def search_all_providers(
    query: Optional[str] = None,
    location: Optional[str] = None,
    limit: int = 30,
    providers: Optional[List[str]] = None,
) -> List[RawJobPosting]:
    """
    Searches across configured job boards and ATS platforms simultaneously.
    """
    chosen_providers = [
        PROVIDERS[p] for p in (providers or PROVIDERS.keys()) if p in PROVIDERS
    ]

    tasks = [p.fetch_jobs(query=query, location=location, limit=limit) for p in chosen_providers]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    combined: List[RawJobPosting] = []
    seen_keys = set()

    for res in results:
        if isinstance(res, list):
            for job in res:
                # Deduplicate by company + title
                key = f"{job.company.lower().strip()}:{job.title.lower().strip()}"
                if key not in seen_keys:
                    seen_keys.add(key)
                    combined.append(job)

    # Sort by posted_at descending if available
    combined.sort(
        key=lambda j: j.posted_at.timestamp() if j.posted_at else 0,
        reverse=True,
    )
    return combined[:limit]


__all__ = [
    "RawJobPosting",
    "BaseJobProvider",
    "RemoteOKProvider",
    "GreenhouseProvider",
    "AshbyProvider",
    "LeverProvider",
    "PROVIDERS",
    "search_all_providers",
    "check_job_liveness",
]
