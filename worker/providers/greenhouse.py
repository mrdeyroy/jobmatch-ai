import httpx
from typing import List, Optional
from datetime import datetime

from worker.providers.base import BaseJobProvider, RawJobPosting, clean_html_to_text


class GreenhouseProvider(BaseJobProvider):
    """
    Scrapes jobs from Greenhouse public boards API:
    https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true
    """
    provider_id = "greenhouse"
    API_URL_TEMPLATE = "https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true"

    # Common tech companies utilizing Greenhouse
    DEFAULT_BOARDS = [
        "stripe",
        "airbnb",
        "figma",
        "cloudflare",
        "pinterest",
        "docker",
        "datadog",
        "elastic",
    ]

    async def fetch_board_jobs(
        self,
        board: str,
        client: httpx.AsyncClient,
        query: Optional[str] = None,
        location: Optional[str] = None,
    ) -> List[RawJobPosting]:
        url = self.API_URL_TEMPLATE.format(board=board)
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
                job_url = j.get("absolute_url", "").strip()
                loc_obj = j.get("location", {})
                loc_name = loc_obj.get("name", "Remote").strip() if isinstance(loc_obj, dict) else "Remote"
                content = j.get("content", "")

                departments = [d.get("name", "") for d in j.get("departments", []) if isinstance(d, dict)]

                searchable = f"{title} {loc_name} {' '.join(departments)} {content}".lower()
                if query_lower and query_lower not in searchable:
                    continue

                if loc_lower and loc_lower not in loc_name.lower():
                    continue

                posted_at = None
                updated_at_str = j.get("updated_at")
                if updated_at_str:
                    try:
                        dt = datetime.fromisoformat(updated_at_str.replace("Z", "+00:00"))
                        posted_at = dt.replace(tzinfo=None)
                    except Exception:
                        posted_at = datetime.utcnow()

                results.append(
                    RawJobPosting(
                        title=title,
                        company=board.capitalize(),
                        location=loc_name or "Remote",
                        url=job_url,
                        description=clean_html_to_text(content),
                        requirements=departments,
                        source="greenhouse",
                        posted_at=posted_at or datetime.utcnow(),
                    )
                )
        except Exception as e:
            print(f"[GreenhouseProvider] Error fetching board {board}: {e}")

        return results

    async def fetch_jobs(
        self,
        query: Optional[str] = None,
        location: Optional[str] = None,
        limit: int = 50,
        boards: Optional[List[str]] = None,
    ) -> List[RawJobPosting]:
        target_boards = boards or self.DEFAULT_BOARDS
        all_jobs: List[RawJobPosting] = []

        async with httpx.AsyncClient(timeout=15.0) as client:
            for board in target_boards:
                board_jobs = await self.fetch_board_jobs(board, client, query, location)
                all_jobs.extend(board_jobs)
                if len(all_jobs) >= limit:
                    break

        return all_jobs[:limit]
