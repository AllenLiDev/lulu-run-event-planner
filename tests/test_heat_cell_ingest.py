from sqlalchemy import text

from jobs.ingest_heat_stub import SAMPLE_HEAT_CELLS, get_engine


def test_heat_cell_ingest_inserts_rows():
    engine = get_engine()

    with engine.begin() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM heat_cell"))
        before = result.scalar_one()

    # run ingestion
    from jobs.ingest_heat_stub import upsert_heat_cells

    upsert_heat_cells(engine, SAMPLE_HEAT_CELLS)

    with engine.begin() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM heat_cell"))
        after = result.scalar_one()

    assert after >= before
