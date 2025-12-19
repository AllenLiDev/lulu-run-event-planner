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
    routes_query = text("""
    SELECT
        r.id,
        r.name,
        r.city,
        r.distance_km,
        s.day_type,
        s.suitability_score,
        s.popularity_score,
        s.accessibility_score,
        s.congestion_penalty,
        s.rationale
    FROM route r
    JOIN route_score s ON s.route_id = r.id
    WHERE s.day_type = :day_type
    ORDER BY s.suitability_score DESC
    LIMIT :limit
""")


    windows_query = text("""
        SELECT start_hour, end_hour, expected_crowd_score
        FROM time_window
        WHERE day_type = :day_type AND city = 'Vancouver'
        ORDER BY expected_crowd_score DESC
    """)

    with engine.begin() as conn:
        routes = conn.execute(
            routes_query,
            {"day_type": day_type, "limit": limit}
        ).mappings().all()

        windows = conn.execute(
            windows_query,
            {"day_type": day_type}
        ).mappings().all()

    return {
        "day_type": day_type,
        "recommended_time_windows": windows,
        "routes": routes,
    }

