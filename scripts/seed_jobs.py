"""Convenience script to seed demo jobs into PostgreSQL."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from worker.ingest import seed

if __name__ == "__main__":
    import asyncio
    asyncio.run(seed())