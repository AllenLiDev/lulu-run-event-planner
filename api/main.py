import os
from dotenv import load_dotenv
from fastapi import FastAPI, Query
from sqlalchemy import create_engine, text

load_dotenv()
engine = create_engine(os.environ["DATABASE_URL"])

app = FastAPI(title="Vancouver Run Event Planner")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/recommendations")
def recommendations(
    day_type: str = Query(default="weekend"),
    limit: int = Query(default=10, ge=1, le=50),
):
    q = text("""
        SELECT r.id, r.name, r.city, r.distance_km,
               s.day_type, s.suitability_score, s.rationale
        FROM route r
        JOIN route_score s ON s.route_id = r.id
        WHERE s.day_type = :day_type
        ORDER BY s.suitability_score DESC
        LIMIT :limit
    """)

    with engine.begin() as conn:
        rows = conn.execute(q, {"day_type": day_type, "limit": limit}).mappings().all()

    return {"results": rows}
