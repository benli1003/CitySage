import psycopg2
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def log_vehicle_count(camera_id: str, count: int) -> bool:
    """
    Logs (or upserts) the vehicle count for the current minute.
    Returns True on success, False on error.
    """
    try:
        conn = psycopg2.connect(
            dbname = os.getenv("DB_NAME"),
            user = os.getenv("DB_USER"),
            password = os.getenv("DB_PASSWORD"),
            host = os.getenv("DB_HOST"),
            port = os.getenv("DB_PORT"),
        )
        cursor = conn.cursor()

        sql = """
        INSERT INTO vehicle_counts (camera_id, timestamp, vehicle_count)
        VALUES (%s, date_trunc('minute', NOW()), %s)
        ON CONFLICT ON CONSTRAINT ux_camera_minute
        DO UPDATE
          SET vehicle_count = vehicle_counts.vehicle_count + EXCLUDED.vehicle_count;
        """

        cursor.execute(sql, (camera_id, count))
        conn.commit()

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"Database error in log_vehicle_count: {e}")
        return False
