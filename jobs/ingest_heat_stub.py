import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

# Load .env for local development
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def get_engine() -> Engine:
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not set")
    return create_engine(DATABASE_URL, future=True)


SAMPLE_HEAT_CELLS = [
    {"cell_id": "cell_001", "lat": 49.2827, "lng": -123.1207, "intensity": 12},
    {"cell_id": "cell_002", "lat": 49.2750, "lng": -123.1210, "intensity": 5},
    {"cell_id": "cell_003", "lat": 49.2630, "lng": -123.1380, "intensity": 20},
]


def upsert_heat_cells(engine: Engine, rows: list[dict]) -> None:
    now = datetime.now(timezone.utc)

    sql = text(
        """
        INSERT INTO heat_cell (cell_id, lat, lng, intensity, updated_at)
        VALUES (:cell_id, :lat, :lng, :intensity, :updated_at)
        ON CONFLICT (cell_id)
        DO UPDATE SET
            lat = EXCLUDED.lat,
            lng = EXCLUDED.lng,
            intensity = EXCLUDED.intensity,
            updated_at = EXCLUDED.updated_at
        """
    )

    payload = [
        {
            "cell_id": r["cell_id"],
            "lat": r["lat"],
            "lng": r["lng"],
            "intensity": r["intensity"],
            "updated_at": now,
        }
        for r in rows
    ]

    with engine.begin() as conn:
        conn.execute(sql, payload)


def main() -> None:
    engine = get_engine()
    upsert_heat_cells(engine, SAMPLE_HEAT_CELLS)
    print(f"Upserted {len(SAMPLE_HEAT_CELLS)} heat cells")


if __name__ == "__main__":
    main()
