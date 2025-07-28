import psycopg2
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def round_time_to_minute(dt):
    return dt.replace(second=0, microsecond=0)

def log_vehicle_count(camera_id, timestamp, count):
    try:
        print(f"Connecting to database: {os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}")
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        cursor = conn.cursor()

        print(f"Executing insert for camera {camera_id}: {count} vehicles at {timestamp}")
        cursor.execute(
            """
            INSERT INTO vehicle_counts (camera_id, timestamp, count)
            VALUES (%s, %s, %s)
            """,
            (camera_id, timestamp, count)
        )

        conn.commit()
        print("Database commit successful")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Database error in log_vehicle_count: {str(e)}")
        return False