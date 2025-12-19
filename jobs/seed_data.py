import os
import json
from uuid import uuid4

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
engine = create_engine(os.environ["DATABASE_URL"])

routes = [
    {"id": str(uuid4()), "name": "Seawall Easy 5K", "city": "Vancouver", "distance_km": 5.0},
    {"id": str(uuid4()), "name": "Stanley Park Loop", "city": "Vancouver", "distance_km": 9.0},
    {"id": str(uuid4()), "name": "Kits Beach Out and Back", "city": "Vancouver", "distance_km": 6.0},
]

def suitability_score(distance_km: float) -> float:
    target = 5.0
    penalty = abs(distance_km - target)
    return round(max(0.0, 1.0 - (penalty / 5.0)), 2)

with engine.begin() as conn:
    for r in routes:
        conn.execute(
            text("""
                INSERT INTO route (id, name, city, distance_km)
                VALUES (:id, :name, :city, :distance_km)
            """),
            r
        )

        rationale = {
            "why_accessible": "Distance close to 5 km, suitable for inclusive community runs",
            "note": "Seed scoring only, heatmap integration coming next"
        }

        conn.execute(
            text("""
                INSERT INTO route_score (route_id, day_type, suitability_score, rationale)
                VALUES (:route_id, :day_type, :score, CAST(:rationale AS jsonb))
            """),
            {
                "route_id": r["id"],
                "day_type": "weekend",
                "score": suitability_score(r["distance_km"]),
                "rationale": json.dumps(rationale),
            }
        )

print("Seed data inserted")
