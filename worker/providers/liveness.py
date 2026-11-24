import httpx
from typing import Optional


async def check_job_liveness(url: str, timeout: float = 6.0) -> bool:
    """
    Zero-token liveness check for a job URL before saving or evaluating it.
    Inspired by career-ops/check-liveness.mjs & liveness-api.mjs.

    Returns:
        True if the job posting is active / accessible.
        False if expired (404, 410, or closed redirect).
    """
    if not url or not url.startswith("http"):
        return False

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            # First try a quick HEAD request
            resp = await client.head(url, headers=headers)
            if resp.status_code in (404, 410):
                return False
            if resp.status_code == 200:
                return True

            # If HEAD is method not allowed (405) or inconclusive, try GET
            if resp.status_code in (405, 403, 301, 302):
                get_resp = await client.get(url, headers=headers)
                if get_resp.status_code in (404, 410):
                    return False
                # Check for common closed markers in title or text
                text_lower = get_resp.text.lower()
                closed_markers = [
                    "this job has expired",
                    "this position has been closed",
                    "this job is no longer available",
                    "posting has expired",
                    "position is filled",
                ]
                if any(marker in text_lower for marker in closed_markers):
                    return False
                return get_resp.status_code < 400

            return resp.status_code < 400
    except Exception:
        # Network timeout or DNS failure: assume conservative False or keep open
        return False
