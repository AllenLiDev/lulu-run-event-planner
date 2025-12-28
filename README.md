# Lululemon Run Event Planner

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
