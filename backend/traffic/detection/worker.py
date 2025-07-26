import cv2
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

from inference import InferencePipeline
from inference.core.interfaces.camera.entities import VideoFrame
from inference.core.interfaces.stream.sinks import render_boxes

load_dotenv()
api_key = os.getenv("ROBOFLOW_API_KEY")

# track for each camera
active_counts = {}
crossed_ids = {}
last_log_time = {}

LINE_POSITION = 300
LINE_COLOR = (0, 0, 255)
LINE_THICKNESS = 2

def start_camera_worker(camera_id: str, stream_url: str):
    global active_counts, crossed_ids, last_log_time

    crossed_ids[camera_id] = set()
    active_counts[camera_id] = 0
    last_log_time[camera_id] = datetime.now()

    def on_prediction(data: dict, frame: VideoFrame):
        predictions = data.get("predictions", [])
        image = frame.image

        for pred in predictions:
            if not isinstance(pred, dict):
                continue

            class_name = pred.get("class_name", "")
            x = pred.get("x", 0)
            y = pred.get("y", 0)
            id_ = pred.get("detection_id")

            if id_ is None:
                continue

            if y > LINE_POSITION and id_ not in crossed_ids[camera_id]:
                crossed_ids[camera_id].add(id_)
                active_counts[camera_id] += 1
                print(f"[{datetime.now().isoformat()}] [{camera_id}] Vehicle crossed line. Total count: {active_counts[camera_id]}")

            print(f"[{camera_id}] Detected: {class_name} at ({x}, {y})")

        # draw line
        cv2.line(image, (0, LINE_POSITION), (image.shape[1], LINE_POSITION), LINE_COLOR, LINE_THICKNESS)
        render_boxes(data, frame)

        # log every minute
        now = datetime.now()
        if now - last_log_time[camera_id] >= timedelta(minutes=1):
            print(f"[{now.isoformat()}] [{camera_id}] Total vehicles in last minute: {active_counts[camera_id]}")
            active_counts[camera_id] = 0
            last_log_time[camera_id] = now

    # pipeline for each camera
    pipeline = InferencePipeline.init(
        model_id = "vehicle_detection_yolov8-rptry/4",
        api_key = api_key,
        video_reference = stream_url,
        on_prediction = on_prediction,
        confidence = 0.3,
        max_fps = 10,
    )

    pipeline.start()
