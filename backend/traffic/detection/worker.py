from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import logging
import warnings

from inference import InferencePipeline
from inference.core.interfaces.camera.entities import VideoFrame
from .database_logger import log_vehicle_count

warnings.filterwarnings("ignore", module="inference")

load_dotenv()
API_KEY = os.getenv("ROBOFLOW_API_KEY")

# Max inference frames/sec per camera. Vehicle line-crossing is reliably
# captured at 1 fps and this is a major driver of EC2 compute cost.
MAX_FPS = int(os.getenv("DETECTION_MAX_FPS", "1"))

logger = logging.getLogger(__name__)

# global state
active_counts = {}
crossed_ids = {}
last_log_time = {}

# virtual counting line (y pixel); a detection below this line counts as a crossing
LINE_POSITION = 300


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

        # log per-minute counts
        if elapsed >= timedelta(minutes=1):
            count = active_counts[camera_id]
            try:
                log_vehicle_count(camera_id, count)
                logger.info("[%s] logged %d vehicles for minute %s",
                            camera_id, count, now.replace(second=0, microsecond=0))
            except Exception as e:
                logger.error("[%s] DB logging error: %s", camera_id, e)

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
    except Exception as e:
        logger.error("[%s] failed to start, camera will be skipped: %s", camera_id, e)
