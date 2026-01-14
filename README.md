# Run Event Planner

A small backend service that recommends Vancouver community run routes using a Postgres data model and a FastAPI API.

## Tech
- Python + FastAPI
- Postgres (Docker)
- SQLAlchemy (for DB connection)

## CI

GitHub Actions runs tests on every pull request and on pushes to master.

If GitHub Actions is unavailable, run the same checks locally:

```bash
python -m pip install -r requirements.txt
python -m pytest
``` 
## Run locally

### 1 Start Postgres
```bash
docker compose up -d
```

### 2 Create Tables
```bash
python jobs/init_db.py
```


### 3 Seed Data
```bash
python jobs/seed_data.py
```

### 4 Start the API
```bash
python -m uvicorn api.main:app --reload
```

### 5 Test Endpoints
```bash
Health: http://127.0.0.1:8000/health
Recommendations: http://127.0.0.1:8000/recommendations
API Docs: http://127.0.0.1:8000/docs
```

## Architecture

Data flow:
1. jobs/init_db.py creates and evolves tables safely using CREATE IF NOT EXISTS and ALTER ADD COLUMN IF NOT EXISTS
2. jobs/seed_data.py seeds routes and writes explainable scoring into route_score
3. jobs/ingest_heat_stub.py upserts heat cells into heat_cell (idempotent, safe to rerun)
4. FastAPI serves /health and /recommendations
5. /recommendations reads precomputed route_score and time_window rows from Postgres

Tables:
- route: canonical route records
- route_score: per route scoring with subscores and a rationale JSON payload
- time_window: recommended time windows by day type
- heat_cell: aggregated heat intensity by geographic cell (ingestion stub today, scoring integration can evolve)

Key design choices:
- Idempotent jobs so reruns and retries are safe
- Explainable scoring via rationale subscores for transparency
- CI enforces formatting, linting, and tests on every PR
