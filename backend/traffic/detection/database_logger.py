import os
import threading
from datetime import datetime
from dotenv import load_dotenv

import psycopg2
from psycopg2.extras import execute_values

load_dotenv()

# A single long-lived connection is reused across writes instead of opening a
# new connection (and TLS handshake) per write. Guarded by a lock because the
# per-camera worker threads share it.
_conn = None
_conn_lock = threading.Lock()


def _connect():
    return psycopg2.connect(
        dbname = os.getenv("DB_NAME"),
        user = os.getenv("DB_USER"),
        password = os.getenv("DB_PASSWORD"),
        host = os.getenv("DB_HOST"),
        port = os.getenv("DB_PORT"),
    )


def _get_conn():
    """Return a live connection, (re)connecting if needed."""
    global _conn
    if _conn is None or _conn.closed:
        _conn = _connect()
    return _conn


# Upsert accumulates counts into the same (camera_id, minute) bucket, so a
# buffered flush produces exactly the same rows as one-at-a-time writes.
_UPSERT_SQL = """
    INSERT INTO vehicle_counts (camera_id, timestamp, "count")
    VALUES %s
    ON CONFLICT (camera_id, timestamp)
    DO UPDATE SET "count" = vehicle_counts."count" + EXCLUDED."count";
"""


def log_vehicle_counts(rows) -> bool:
    """
    Batch-upsert per-minute vehicle counts in a single query on a reused
    connection.

    `rows` is an iterable of (camera_id: str, minute_ts: datetime, count: int).
    The timestamp is passed explicitly (not NOW()) so counts land in the minute
    bucket they were observed in, even when flushed later. Returns True on
    success, False on error.
    """
    rows = [r for r in rows if r is not None]
    if not rows:
        return True

    with _conn_lock:
        try:
            conn = _get_conn()
            with conn.cursor() as cursor:
                execute_values(cursor, _UPSERT_SQL, rows)
            conn.commit()
            return True
        except Exception as e:
            print(f"Database error in log_vehicle_counts: {e}")
            # Drop the (possibly broken) connection so the next call reconnects.
            global _conn
            try:
                if _conn is not None:
                    _conn.close()
            except Exception:
                pass
            _conn = None
            return False


def log_vehicle_count(camera_id: str, count: int) -> bool:
    """
    Backwards-compatible single-row write. Logs `count` for the current minute.
    Prefer log_vehicle_counts() for batched flushes.
    """
    minute_ts = datetime.now().replace(second=0, microsecond=0)
    return log_vehicle_counts([(camera_id, minute_ts, count)])
