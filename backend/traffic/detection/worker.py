import cv2
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import logging
import warnings

from inference import InferencePipeline
from inference.core.interfaces.camera.entities import VideoFrame
from inference.core.interfaces.stream.sinks import render_boxes
from .database_logger import log_vehicle_count

warnings.filterwarnings("ignore", module="inference")
logging.getLogger("inference.core.interfaces.stream.sinks").setLevel(logging.CRITICAL)

load_dotenv()
API_KEY = os.getenv("ROBOFLOW_API_KEY")

# global state
active_counts = {}
crossed_ids = {}
last_log_time = {}

# line parameters
LINE_POSITION = 300
LINE_COLOR = (0, 0, 255)
LINE_THICKNESS = 2


def start_camera_worker(camera_id: str, stream_url: str):
    global active_counts, crossed_ids, last_log_time

    crossed_ids[camera_id] = set()
    active_counts[camera_id] = 0
    last_log_time[camera_id] = datetime.now()
    
    print(f"[{camera_id}] Starting camera worker...")

    def on_prediction(data: dict, frame: VideoFrame):
        now = datetime.now()
        elapsed = now - last_log_time[camera_id]
        preds = data.get("predictions", [])
        img = frame.image

        # count crossings
        for pred in preds:
            if not isinstance(pred, dict):
                continue

            x, y = pred.get("x", 0), pred.get("y", 0)
            id_ = pred.get("detection_id")
            if id_ is None:
                continue

            if y > LINE_POSITION and id_ not in crossed_ids[camera_id]:
                crossed_ids[camera_id].add(id_)
                active_counts[camera_id] += 1
                print(f"[{now.isoformat()}] [{camera_id}] Vehicle crossed line (count={active_counts[camera_id]})")

        # draw line and boxes
        cv2.line(img, (0, LINE_POSITION), (img.shape[1], LINE_POSITION), LINE_COLOR, LINE_THICKNESS)
        try:
            render_boxes(data, frame)
        except Exception:
            pass

        # log per-minute counts
        if elapsed >= timedelta(minutes=1):
            count = active_counts[camera_id]
            try:
                log_vehicle_count(camera_id, count)
                ts = now.replace(second=0, microsecond=0)
                print(f"Logged {count} vehicles at {ts}")
            except Exception as e:
                print(f"DB logging error: {e}")

            active_counts[camera_id] = 0
            last_log_time[camera_id] = now

    try:
        print(f"[{camera_id}] Initializing inference pipeline...")
        pipeline = InferencePipeline.init(
            model_id = "vehicle_detection_yolov8-rptry/4",
            api_key = API_KEY,
            video_reference = stream_url,
            on_prediction = on_prediction,
            confidence = 0.3,
            max_fps = 10,
        )
        print(f"[{camera_id}] Pipeline initialized successfully")
        pipeline.start()
        print(f"[{camera_id}] Camera detection started")
    except Exception as e:
        print(f"[{camera_id}] Failed to start: {str(e)}")
        print(f"[{camera_id}] Camera will be skipped")
