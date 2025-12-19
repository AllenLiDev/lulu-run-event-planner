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

def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))

def calc_accessibility(distance_km: float) -> float:
    # Inclusive community run target is ~5K
    target = 5.0
    penalty = abs(distance_km - target) / 5.0
    return round(clamp01(1.0 - penalty), 2)

def calc_popularity_seed(name: str) -> float:
    # Placeholder until heatmap integration.
    # Just making the seed data feel realistic.
    if "Seawall" in name:
        return 0.9
    if "Stanley" in name:
        return 0.85
    return 0.7

def calc_congestion_seed(popularity: float) -> float:
    # Simple proxy: very popular routes can have crowding hotspots
    return round(clamp01(popularity * 0.6), 2)

def calc_suitability(popularity: float, accessibility: float, congestion: float) -> float:
    suitability = (0.55 * popularity) + (0.35 * accessibility) - (0.30 * congestion)
    return round(clamp01(suitability), 2)

with engine.begin() as conn:
    # Make reruns safe
    conn.execute(text("DELETE FROM route_score"))
    conn.execute(text("DELETE FROM route"))

    for r in routes:
        conn.execute(
            text("""
                INSERT INTO route (id, name, city, distance_km)
                VALUES (:id, :name, :city, :distance_km)
            """),
            r
        )

        popularity = calc_popularity_seed(r["name"])
        accessibility = calc_accessibility(float(r["distance_km"]))
        congestion = calc_congestion_seed(popularity)
        suitability = calc_suitability(popularity, accessibility, congestion)

        rationale = {
            "summary": "Balanced option for a community run based on popularity and accessibility.",
            "subscores": {
                "popularity_score": popularity,
                "accessibility_score": accessibility,
                "congestion_penalty": congestion
            },
            "notes": [
                "Seed scoring uses placeholder popularity and congestion signals until heatmap integration."
            ]
        }

        conn.execute(
            text("""
                INSERT INTO route_score (
                    route_id, day_type, suitability_score, rationale,
                    popularity_score, accessibility_score, congestion_penalty
                )
                VALUES (
                    :route_id, :day_type, :suitability, CAST(:rationale AS jsonb),
                    :popularity, :accessibility, :congestion
                )
            """),
            {
                "route_id": r["id"],
                "day_type": "weekend",
                "suitability": suitability,
                "rationale": json.dumps(rationale),
                "popularity": popularity,
                "accessibility": accessibility,
                "congestion": congestion,
            }
        )

print("Seed data inserted with subscores")
