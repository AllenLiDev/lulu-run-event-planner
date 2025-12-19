import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(DATABASE_URL)

DDL = """
CREATE TABLE IF NOT EXISTS route (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  city TEXT NOT NULL,
  distance_km NUMERIC NOT NULL
);

CREATE TABLE IF NOT EXISTS route_score (
  route_id TEXT PRIMARY KEY REFERENCES route(id),
  day_type TEXT NOT NULL,
  suitability_score NUMERIC NOT NULL,
  rationale JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS time_window (
  id SERIAL PRIMARY KEY,
  city TEXT NOT NULL,
  day_type TEXT NOT NULL,
  start_hour INT NOT NULL,
  end_hour INT NOT NULL,
  expected_crowd_score NUMERIC NOT NULL
);
"""

with engine.begin() as conn:
    conn.execute(text(DDL))

print("DB initialized")
