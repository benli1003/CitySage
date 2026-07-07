from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import logging
import threading
import time
import warnings

from inference import InferencePipeline
from inference.core.interfaces.camera.entities import VideoFrame
from .database_logger import log_vehicle_counts

warnings.filterwarnings("ignore", module="inference")

load_dotenv()
API_KEY = os.getenv("ROBOFLOW_API_KEY")

# Max inference frames/sec per camera. Vehicle line-crossing is reliably
# captured at 1 fps and this is a major driver of EC2 compute cost.
MAX_FPS = int(os.getenv("DETECTION_MAX_FPS", "1"))

# How often the buffered per-minute counts are flushed to the DB, in one
# batched write for the whole fleet, instead of a write per camera per minute.
FLUSH_INTERVAL_SECONDS = int(os.getenv("DB_FLUSH_INTERVAL_SECONDS", "600"))

logger = logging.getLogger(__name__)

# global state
active_counts = {}
crossed_ids = {}
last_log_time = {}

# Buffer of closed-minute counts pending a batched DB flush, keyed by
# (camera_id, minute_ts) so late flushes still land in the correct minute
# bucket. Shared across worker threads, so guarded by a lock.
_pending = {}
_pending_lock = threading.Lock()
_flusher_started = False

# virtual counting line (y pixel); a detection below this line counts as a crossing
LINE_POSITION = 300


def _buffer_count(camera_id: str, minute_ts: datetime, count: int):
    """Accumulate a closed minute's count into the pending flush buffer."""
    with _pending_lock:
        key = (camera_id, minute_ts)
        _pending[key] = _pending.get(key, 0) + count


def flush_pending_counts() -> bool:
    """Drain the buffer and write all pending minute counts in one batch."""
    with _pending_lock:
        if not _pending:
            return True
        rows = [(cam, ts, cnt) for (cam, ts), cnt in _pending.items()]
        snapshot = dict(_pending)
        _pending.clear()

    ok = log_vehicle_counts(rows)
    if ok:
        logger.info("flushed %d camera-minute rows to DB", len(rows))
    else:
        # Re-buffer on failure so the counts are retried on the next flush.
        with _pending_lock:
            for (cam, ts), cnt in snapshot.items():
                _pending[(cam, ts)] = _pending.get((cam, ts), 0) + cnt
        logger.error("batch flush failed; %d rows re-buffered for retry", len(rows))
    return ok


def _flush_loop():
    while True:
        time.sleep(FLUSH_INTERVAL_SECONDS)
        try:
            flush_pending_counts()
        except Exception as e:
            logger.error("flush loop error: %s", e)


def start_flusher():
    """Start the background batch-flush thread once."""
    global _flusher_started
    if _flusher_started:
        return
    _flusher_started = True
    threading.Thread(target=_flush_loop, daemon=True).start()
    logger.info("DB batch flusher started (interval=%ds)", FLUSH_INTERVAL_SECONDS)


def start_camera_worker(camera_id: str, stream_url: str):
    global active_counts, crossed_ids, last_log_time

    crossed_ids[camera_id] = set()
    active_counts[camera_id] = 0
    last_log_time[camera_id] = datetime.now()
    
    logger.info("[%s] starting camera worker", camera_id)

    def on_prediction(data: dict, frame: VideoFrame):
        now = datetime.now()
        elapsed = now - last_log_time[camera_id]
        preds = data.get("predictions", [])

        # count crossings
        for pred in preds:
            if not isinstance(pred, dict):
                continue

            y = pred.get("y", 0)
            id_ = pred.get("detection_id")
            if id_ is None:
                continue

            if y > LINE_POSITION and id_ not in crossed_ids[camera_id]:
                crossed_ids[camera_id].add(id_)
                active_counts[camera_id] += 1
                logger.debug("[%s] vehicle crossed (count=%d)", camera_id, active_counts[camera_id])

        # Note: no frame annotation here. This is a headless server, so drawing
        # boxes/lines onto the frame was pure wasted CPU (~fps x cameras/sec).

        # buffer the closed minute's count; a background thread flushes the
        # whole fleet to the DB in one batched write (see start_flusher).
        if elapsed >= timedelta(minutes=1):
            count = active_counts[camera_id]
            minute_ts = last_log_time[camera_id].replace(second=0, microsecond=0)
            _buffer_count(camera_id, minute_ts, count)
            logger.debug("[%s] buffered %d vehicles for minute %s",
                         camera_id, count, minute_ts)

            active_counts[camera_id] = 0
            last_log_time[camera_id] = now

    try:
        logger.info("[%s] initializing inference pipeline (max_fps=%d)", camera_id, MAX_FPS)
        pipeline = InferencePipeline.init(
            model_id = "vehicle_detection_yolov8-rptry/4",
            api_key = API_KEY,
            video_reference = stream_url,
            on_prediction = on_prediction,
            confidence = 0.3,
            max_fps = MAX_FPS,
        )
        pipeline.start()
        logger.info("[%s] camera detection started", camera_id)
        return pipeline
    except Exception as e:
        logger.error("[%s] failed to start, camera will be skipped: %s", camera_id, e)
        return None


def stop_camera_worker(camera_id: str, pipeline):
    """Stop a running pipeline and buffer any partial in-progress count."""
    if pipeline is not None:
        try:
            pipeline.terminate()
            pipeline.join()
        except Exception as e:
            logger.error("[%s] error stopping pipeline: %s", camera_id, e)

    # Flush the partial minute so an in-progress count isn't dropped on cycle.
    count = active_counts.get(camera_id, 0)
    if count > 0:
        minute_ts = last_log_time.get(camera_id, datetime.now()).replace(second=0, microsecond=0)
        _buffer_count(camera_id, minute_ts, count)
        active_counts[camera_id] = 0
    logger.info("[%s] camera detection stopped", camera_id)
