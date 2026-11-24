# JobMatch AI 

AI-powered career platform for students and early-career job seekers.  
**Multi-Platform Job Search • Live ATS Scrapers • Personalized Job Matching • ATS Résumé Scoring • JD-Aware CV Tailoring • Streamlit Web UI**

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32-red)](https://streamlit.io/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)](https://www.postgresql.org/)
[![pgvector](https://img.shields.io/badge/pgvector-0.3-purple)](https://github.com/pgvector/pgvector)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue)](https://www.docker.com/)

---

## About

**JobMatch AI** is an end-to-end AI career platform designed to mirror a real-world production job search and career matching application. It helps candidates:

- **Search jobs live across major ATS platforms** (Greenhouse, Ashby, Lever, RemoteOK) without third-party scraping APIs.
- **Filter out expired or ghost jobs** with zero-token HTTP HEAD/GET liveness checks before saving or evaluating.
- **Index and search jobs semantically** in PostgreSQL with pgvector embeddings and full-text keyword filtering.
- **Match profiles to jobs** with score explanations based on user skills and target roles.
- **Score résumés for ATS friendliness (0–100)** across formatting, keywords, sections, and readability.
- **Receive JD-aware CV tailoring** suggestions with anti-hallucination guardrails.
- **Interact visually** through an intuitive Streamlit Web UI or integrate via a modular FastAPI REST backend.

This project is **local-first** and fully containerized with Docker Compose.

---

## Features

| Feature | Description |
|---------|-------------|
| **Multi-Platform Job Search** | Zero-token direct search across Greenhouse, Ashby, Lever, and RemoteOK feeds. |
| **Liveness Verification** | Automatic verification of job URLs to detect closed, expired, or 404 postings. |
| **Hybrid Job Search** | PostgreSQL full-text search combined with pgvector vector embeddings. |
| **Personalized Matching** | Matches user profile skills and preferred roles against job requirements with natural-language explanations. |
| **Interactive Streamlit Web UI** | Web dashboard to search live jobs, trigger ingestion batches, view job descriptions, and test ATS scoring. |
| **ATS Scorer Agent** | Analyzes PDF/DOCX résumés, scoring 0–100 across formatting, keywords, sections, and readability. |
| **CV Tailor Agent** | Generates targeted before/after bullet revisions aligned with job descriptions. |
| **Containerized Stack** | Full Docker Compose orchestration (FastAPI + Streamlit + PostgreSQL/pgvector). |

---

## Tech Stack

- **Backend:** Python 3.11, FastAPI, SQLAlchemy 2.0 (asyncio + asyncpg)
- **Frontend:** Streamlit 1.32
- **Database:** PostgreSQL 16 + pgvector (HNSW vector indexing)
- **Scraping & Ingestion:** Async HTTP (`httpx`), public ATS endpoints (Greenhouse, Ashby, Lever, RemoteOK)
- **LLM / AI:** OpenAI API (structured Pydantic outputs)
- **Containerization:** Docker & Docker Compose

---

## Project Structure

```
jobmatch-ai/
├── apps/
│   ├── api/
│   │   ├── main.py                   # FastAPI application entrypoint & routers
│   │   ├── schemas.py                # Pydantic schemas (JobOut, JobSearchRequest, etc.)
│   │   ├── db/
│   │   │   ├── session.py            # Async SQLAlchemy engine & session maker
│   │   │   └── models.py             # SQLAlchemy models (Job, User, Profile, ATSReport, etc.)
│   │   ├── routers/
│   │   │   ├── jobs.py               # /jobs/search, /jobs/match, /jobs/ingest
│   │   │   ├── ats.py                # /ats/score
│   │   │   ├── cv.py                 # /cv/tailor
│   │   │   ├── agent.py              # /agent/chat
│   │   │   └── feedback.py           # /feedback
│   │   └── agents/
│   │       ├── ats_agent.py          # ATS-friendliness evaluation agent
│   │       ├── cv_tailor.py          # JD-aware CV tailoring agent
│   │       └── career_agent.py       # Career chat assistant
│   └── ui.py                         # Streamlit interactive Web UI
├── worker/
│   ├── ingest.py                     # Job ingestion pipeline & CLI runner
│   ├── embed.py                      # Embedding generation worker
│   └── providers/                    # Multi-platform ATS scrapers
│       ├── base.py                   # BaseJobProvider, RawJobPosting, HTML strip pipeline
│       ├── greenhouse.py             # Greenhouse public boards scraper
│       ├── ashby.py                  # Ashby posting API scraper (with compensation)
│       ├── lever.py                  # Lever postings API scraper
│       ├── remoteok.py               # RemoteOK public feed aggregator
│       └── liveness.py               # Zero-token HTTP link liveness verifier
├── scripts/
│   └── seed_jobs.py                  # Seed demo and live jobs into PostgreSQL
├── evals/
│   ├── golden_set.jsonl              # Annotated CV/JD pairs for evaluation
│   ├── judge_prompt.txt              # LLM-as-a-judge rubric
│   └── run_eval.py                   # Offline eval runner
├── Dockerfile                        # Multi-stage Python container
├── docker-compose.yml                # api + frontend + db orchestration
├── requirements.txt                  # Python dependencies
└── README.md
```

---

## Quick Start with Docker

### Prerequisites
- Docker and Docker Compose installed
- (Optional) An OpenAI API key in `.env` for AI evaluation endpoints

### 1. Start All Services

```bash
# Clone the repository
git clone https://github.com/abhishek-ngu/CareerPath-AI-AI-Career-Job-Matching-Platform.git
cd CareerPath-AI-AI-Career-Job-Matching-Platform

# Copy environment template
cp .env.example .env

# Build and start services (API, Streamlit UI, PostgreSQL)
docker compose up --build -d
```

### 2. Access the Applications

* **Streamlit Web UI:** [http://localhost:8501](http://localhost:8501)
* **FastAPI Backend:** [http://localhost:8000](http://localhost:8000)
* **Interactive Swagger Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **PostgreSQL (pgvector):** `localhost:5432` (`user: careerpath`, `password: careerpath`, `db: careerpath`)

---

## Ingesting Jobs

You can ingest live jobs from Greenhouse, Ashby, Lever, and RemoteOK at any time:

### Via Web UI
Navigate to the **"📥 Ingest Jobs"** tab at [http://localhost:8501](http://localhost:8501), enter a search keyword (e.g. `Engineer`, `Python`, `Remote`), and click **Start Ingestion**.

### Via API Endpoint
```bash
curl -X POST http://localhost:8000/jobs/ingest \
  -H "Content-Type: application/json" \
  -d '{"query": "python", "limit": 20}'
```

### Via CLI Inside the Container
```bash
docker exec -it jobmatch-ai-api-1 python -m worker.ingest --query "backend" --limit 15 --verify-liveness
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | API health check |
| `/jobs/search` | POST | Search jobs (set `"live": true` for real-time external platforms, or `"live": false` for PostgreSQL index) |
| `/jobs/ingest` | POST | Ingest live jobs across platforms into PostgreSQL |
| `/jobs/match` | POST | Personalized job matching against user profile with explanations |
| `/ats/score` | POST | ATS résumé scoring (0–100) across formatting & keywords |
| `/cv/tailor` | POST | JD-aware CV before/after revision suggestions |
| `/agent/chat` | POST | Career conversation agent |
| `/feedback` | POST | Submit thumbs-up/down user feedback |

### Example: Live Multi-Platform Search

```bash
curl -X POST http://localhost:8000/jobs/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Software Engineer",
    "location": "Remote",
    "limit": 5,
    "live": true
  }'
```

---

## Offline Evaluation Pipeline

The evaluation pipeline is located in `evals/`:
- `golden_set.jsonl`: Annotated CV/job-description test pairs.
- `judge_prompt.txt`: Evaluation rubric for LLM-as-a-judge scoring.
- `run_eval.py`: Script to run evaluation benchmarks in CI.
