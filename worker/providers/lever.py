import httpx
from typing import List, Optional
from datetime import datetime

from worker.providers.base import BaseJobProvider, RawJobPosting, clean_html_to_text


class LeverProvider(BaseJobProvider):
    """
    Scrapes jobs from Lever public postings API:
    https://api.lever.co/v0/postings/{slug}?mode=json
    """
    provider_id = "lever"
    API_URL_TEMPLATE = "https://api.lever.co/v0/postings/{slug}?mode=json"

    DEFAULT_SLUGS = [
        "netflix",
        "spotify",
        "palantir",
    ]

    async def fetch_slug_jobs(
        self,
        slug: str,
        client: httpx.AsyncClient,
        query: Optional[str] = None,
        location: Optional[str] = None,
    ) -> List[RawJobPosting]:
        url = self.API_URL_TEMPLATE.format(slug=slug)
        results: List[RawJobPosting] = []

        try:
            resp = await client.get(url)
            if resp.status_code != 200:
                return results

            raw_jobs = resp.json()
            if not isinstance(raw_jobs, list):
                return results

            query_lower = query.lower().strip() if query else None
            loc_lower = location.lower().strip() if location else None

            for j in raw_jobs:
                if not isinstance(j, dict):
                    continue

                title = j.get("text", "").strip()
                hosted_url = j.get("hostedUrl", "").strip()
                apply_url = j.get("applyUrl", "").strip() or hosted_url
                categories = j.get("categories", {})

                loc_name = categories.get("location", "Remote").strip() if isinstance(categories, dict) else "Remote"
                workplace_type = j.get("workplaceType", "")
                if workplace_type and workplace_type.lower() == "remote" and "remote" not in loc_name.lower():
                    loc_name = f"{loc_name} (Remote)".strip()

                desc_plain = j.get("descriptionPlain", "")
                desc_html = j.get("description", "")
                team = categories.get("team", "") if isinstance(categories, dict) else ""

                searchable = f"{title} {loc_name} {team} {desc_plain}".lower()
                if query_lower and query_lower not in searchable:
                    continue

                if loc_lower and loc_lower not in loc_name.lower():
                    continue

                posted_at = None
                created_at_epoch = j.get("createdAt")
                if isinstance(created_at_epoch, (int, float)):
                    try:
                        posted_at = datetime.fromtimestamp(created_at_epoch / 1000.0)
                    except Exception:
                        posted_at = datetime.utcnow()

                clean_desc = desc_plain if desc_plain else clean_html_to_text(desc_html)
                reqs = [team] if team else []

                results.append(
                    RawJobPosting(
                        title=title,
                        company=slug.capitalize(),
                        location=loc_name or "Remote",
                        url=apply_url,
                        description=clean_desc[:5000],
                        requirements=reqs,
                        source="lever",
                        posted_at=posted_at or datetime.utcnow(),
                    )
                )
        except Exception as e:
            print(f"[LeverProvider] Error fetching slug {slug}: {e}")

        return results

    async def fetch_jobs(
        self,
        query: Optional[str] = None,
        location: Optional[str] = None,
        limit: int = 50,
        slugs: Optional[List[str]] = None,
    ) -> List[RawJobPosting]:
        target_slugs = slugs or self.DEFAULT_SLUGS
        all_jobs: List[RawJobPosting] = []

        async with httpx.AsyncClient(timeout=20.0) as client:
            for slug in target_slugs:
                slug_jobs = await self.fetch_slug_jobs(slug, client, query, location)
                all_jobs.extend(slug_jobs)
                if len(all_jobs) >= limit:
                    break

        return all_jobs[:limit]
