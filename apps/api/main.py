from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.api.db.session import init_db
from apps.api.routers import jobs, ats, cv, agent, feedback


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="CareerPath AI",
    version="0.1.0",
    description="AI career platform: semantic search, job matching, ATS scorer, CV tailor",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
app.include_router(ats.router, prefix="/ats", tags=["ats"])
app.include_router(cv.router, prefix="/cv", tags=["cv"])
app.include_router(agent.router, prefix="/agent", tags=["agent"])
app.include_router(feedback.router, prefix="/feedback", tags=["feedback"])


@app.get("/health")
async def health():
    return {"status": "ok"}