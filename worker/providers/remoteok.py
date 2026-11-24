import httpx
from typing import List, Optional
from datetime import datetime

from worker.providers.base import BaseJobProvider, RawJobPosting, clean_html_to_text


class RemoteOKProvider(BaseJobProvider):
    """
    Scrapes live jobs from RemoteOK public API feed (https://remoteok.com/api).
    Zero-token direct aggregator returning 100+ fresh remote listings.
    """
    provider_id = "remoteok"
    FEED_URL = "https://remoteok.com/api"

    async def fetch_jobs(
        self,
        query: Optional[str] = None,
        location: Optional[str] = None,
        limit: int = 50,
    ) -> List[RawJobPosting]:
        headers = {
            "User-Agent": "JobMatchAI/1.0 (Job Aggregator)",
            "Accept": "application/json",
        }
        jobs: List[RawJobPosting] = []

        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=False) as client:
                resp = await client.get(self.FEED_URL, headers=headers)
                if resp.status_code != 200:
                    return jobs

                data = resp.json()
                if not isinstance(data, list):
                    return jobs

                # The first item in RemoteOK is metadata/legal info
                items = data[1:]

                query_lower = query.lower().strip() if query else None
                loc_lower = location.lower().strip() if location else None

                for item in items:
                    if not isinstance(item, dict):
                        continue

                    title = item.get("position", "").strip()
                    url = item.get("url", "").strip()
                    company = item.get("company", "RemoteOK").strip()
                    loc = item.get("location", "Remote").strip() or "Remote"
                    raw_desc = item.get("description", "")
                    tags = item.get("tags", [])
                    if isinstance(tags, list):
                        reqs = [str(t).strip() for t in tags if str(t).strip()]
                    else:
                        reqs = []

                    if not title or not url:
                        continue

                    # Filter by query if specified
                    searchable_text = f"{title} {' '.join(reqs)} {company} {raw_desc}".lower()
                    if query_lower and query_lower not in searchable_text:
                        continue

                    # Filter by location if specified
                    if loc_lower and loc_lower not in loc.lower() and "remote" not in loc.lower():
                        continue

                    posted_at = None
                    date_str = item.get("date")
                    if date_str:
                        try:
                            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                            posted_at = dt.replace(tzinfo=None)
                        except Exception:
                            posted_at = datetime.utcnow()

                    clean_desc = clean_html_to_text(raw_desc)

                    jobs.append(
                        RawJobPosting(
                            title=title,
                            company=company,
                            location=loc,
                            url=url,
                            description=clean_desc,
                            requirements=reqs,
                            source="remoteok",
                            posted_at=posted_at or datetime.utcnow(),
                        )
                    )

                    if len(jobs) >= limit:
                        break

        except Exception as e:
            print(f"[RemoteOKProvider] Error fetching jobs: {e}")

        return jobs
