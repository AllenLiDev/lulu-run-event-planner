import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
engine = create_engine(os.environ["DATABASE_URL"])

CITY = "Vancouver"

windows = [
    # Weekday: early morning and after work
    {"city": CITY, "day_type": "weekday", "start_hour": 6, "end_hour": 8, "expected_crowd_score": 0.55},
    {"city": CITY, "day_type": "weekday", "start_hour": 18, "end_hour": 20, "expected_crowd_score": 0.70},

    # Weekend: mid-morning tends to be popular for group runs
    {"city": CITY, "day_type": "weekend", "start_hour": 8, "end_hour": 11, "expected_crowd_score": 0.80},
]

with engine.begin() as conn:
    # Make this idempotent: clear and reinsert for this city
    conn.execute(
        text("DELETE FROM time_window WHERE city = :city"),
        {"city": CITY}
    )

    for w in windows:
        conn.execute(
            text("""
                INSERT INTO time_window (city, day_type, start_hour, end_hour, expected_crowd_score)
                VALUES (:city, :day_type, :start_hour, :end_hour, :expected_crowd_score)
            """),
            w
        )

print("Time windows seeded")
