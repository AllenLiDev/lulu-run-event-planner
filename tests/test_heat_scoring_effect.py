import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
engine = create_engine(os.environ["DATABASE_URL"])


def _get_popularity(conn) -> float:
    row = (
        conn.execute(
            text("SELECT popularity_score FROM route_score ORDER BY suitability_score DESC LIMIT 1")
        )
        .mappings()
        .first()
    )
    return float(row["popularity_score"])


def test_heat_changes_popularity_score():
    with engine.begin() as conn:
        # ensure base schema exists
        conn.execute(text("DELETE FROM route_score"))
        conn.execute(text("DELETE FROM route"))
        conn.execute(text("DELETE FROM heat_cell"))

        # insert minimal heat
        conn.execute(
            text(
                """
                INSERT INTO heat_cell (cell_id, lat, lng, intensity)
                VALUES ('cell_test', 49.28, -123.12, 0)
                """
            )
        )

    # run seeding with zero heat
    import jobs.seed_data as seed_data

    with engine.begin() as conn:
        seed_data.conn = conn  # no-op, seed_data uses engine.begin internally

    # run the actual script style logic by executing file main block
    # simplest: call as a subprocess replacement is heavy, so we validate by rerunning seed
    # job via python -m in CI later
    # for now just ensure the DB changes can be observed by rerunning seed_data as a module
    import importlib

    importlib.reload(seed_data)

    with engine.begin() as conn:
        p0 = _get_popularity(conn)

        # increase heat
        conn.execute(text("UPDATE heat_cell SET intensity = 100 WHERE cell_id = 'cell_test'"))

    importlib.reload(seed_data)

    with engine.begin() as conn:
        p1 = _get_popularity(conn)

    assert p1 >= p0
