"""Stub: generate embeddings for jobs and upsert into pgvector index."""
import asyncio

from apps.api.db.session import async_session
from apps.api.db.models import Job
from sqlalchemy import select

TODO_NOTE = """
TODO:
1. Fetch jobs where embedding IS NULL
2. Call OpenAI embeddings API (text-embedding-3-small or BGE)
3. Upsert vector into jobs.embedding column (Vector(1536))
4. Schedule incremental refresh for "constantly changing" index
"""


async def embed_jobs():
    print(TODO_NOTE)


if __name__ == "__main__":
    asyncio.run(embed_jobs())