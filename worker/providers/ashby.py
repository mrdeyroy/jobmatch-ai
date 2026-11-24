import httpx
from typing import List, Optional, Dict, Any
from datetime import datetime

from worker.providers.base import BaseJobProvider, RawJobPosting, clean_html_to_text


class AshbyProvider(BaseJobProvider):
    """
    Scrapes jobs from Ashby posting API:
    https://api.ashbyhq.com/posting-api/job-board/{org}?includeCompensation=true
    """
    provider_id = "ashby"
    API_URL_TEMPLATE = "https://api.ashbyhq.com/posting-api/job-board/{org}?includeCompensation=true"

    DEFAULT_ORGS = [
        "openai",
        "retool",
        "ramp",
        "linear",
        "supabase",
        "mistral-ai",
        "anysphere",
    ]

    async def fetch_org_jobs(
        self,
        org: str,
        client: httpx.AsyncClient,
        query: Optional[str] = None,
        location: Optional[str] = None,
    ) -> List[RawJobPosting]:
        url = self.API_URL_TEMPLATE.format(org=org)
        results: List[RawJobPosting] = []

        try:
            resp = await client.get(url)
            if resp.status_code != 200:
                return results

            data = resp.json()
            raw_jobs = data.get("jobs", [])

            query_lower = query.lower().strip() if query else None
            loc_lower = location.lower().strip() if location else None

            for j in raw_jobs:
                title = j.get("title", "").strip()
                apply_url = j.get("applyUrl", "").strip() or j.get("jobUrl", "").strip()
                loc_name = j.get("location", "Remote").strip() or "Remote"
                if j.get("isRemote"):
                    loc_name = f"{loc_name} (Remote)".strip()

                desc_html = j.get("descriptionHtml", "")
                desc_plain = j.get("descriptionPlain", "")
                dept = j.get("department", "")

                searchable = f"{title} {loc_name} {dept} {desc_plain}".lower()
                if query_lower and query_lower not in searchable:
                    continue

                if loc_lower and loc_lower not in loc_name.lower():
                    continue

                posted_at = None
                published_at_str = j.get("publishedAt")
                if published_at_str:
                    try:
                        dt = datetime.fromisoformat(published_at_str.replace("Z", "+00:00"))
                        posted_at = dt.replace(tzinfo=None)
                    except Exception:
                        posted_at = datetime.utcnow()

                clean_desc = desc_plain if desc_plain else clean_html_to_text(desc_html)

                requirements = [dept] if dept else []
                # Also capture compensation info if present
                comp = j.get("compensation")
                if isinstance(comp, dict) and comp.get("summary"):
                    requirements.append(f"Comp: {comp.get('summary')}")

                results.append(
                    RawJobPosting(
                        title=title,
                        company=org.capitalize(),
                        location=loc_name,
                        url=apply_url,
                        description=clean_desc[:5000],
                        requirements=requirements,
                        source="ashby",
                        posted_at=posted_at or datetime.utcnow(),
                    )
                )
        except Exception as e:
            print(f"[AshbyProvider] Error fetching org {org}: {e}")

        return results

    async def fetch_jobs(
        self,
        query: Optional[str] = None,
        location: Optional[str] = None,
        limit: int = 50,
        orgs: Optional[List[str]] = None,
    ) -> List[RawJobPosting]:
        target_orgs = orgs or self.DEFAULT_ORGS
        all_jobs: List[RawJobPosting] = []

        async with httpx.AsyncClient(timeout=20.0) as client:
            for org in target_orgs:
                org_jobs = await self.fetch_org_jobs(org, client, query, location)
                all_jobs.extend(org_jobs)
                if len(all_jobs) >= limit:
                    break

        return all_jobs[:limit]
