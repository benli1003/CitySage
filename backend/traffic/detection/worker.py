import cv2
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import logging
import warnings
import threading
import time

import numpy as np
from ultralytics import YOLO
import supervision as sv
from .database_logger import log_vehicle_count

warnings.filterwarnings("ignore")
logging.getLogger("ultralytics").setLevel(logging.CRITICAL)

load_dotenv()

# COCO class IDs for vehicles: car=2, motorcycle=3, bus=5, truck=7
VEHICLE_CLASSES = {2, 3, 5, 7}

# global state
active_counts = {}
crossed_ids = {}
last_log_time = {}

# line parameters
LINE_POSITION = 300
LINE_COLOR = (0, 0, 255)
LINE_THICKNESS = 2

# shared model (loaded once)
_model = None
_model_lock = threading.Lock()

def _get_model():
    global _model
    with _model_lock:
        if _model is None:
            model_path = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "models", "yolov8n.pt")
            model_path = os.path.normpath(model_path)
            _model = YOLO(model_path)
    return _model


def start_camera_worker(camera_id: str, stream_url: str):
    global active_counts, crossed_ids, last_log_time

    crossed_ids[camera_id] = set()
    active_counts[camera_id] = 0
    last_log_time[camera_id] = datetime.now()

    print(f"[{camera_id}] Starting camera worker...")

    model = _get_model()
    tracker = sv.ByteTrack()
    box_annotator = sv.BoxAnnotator()

    cap = cv2.VideoCapture(stream_url)
    if not cap.isOpened():
        print(f"[{camera_id}] Failed to open stream: {stream_url}")
        return

    print(f"[{camera_id}] Camera detection started")

    frame_interval = 1.0 / 3  # ~3 fps
    last_frame_time = 0.0

    while True:
        ret, frame = cap.read()
        if not ret:
            print(f"[{camera_id}] Stream ended or error, retrying...")
            time.sleep(5)
            cap.release()
            cap = cv2.VideoCapture(stream_url)
            continue

        now_ts = time.time()
        if now_ts - last_frame_time < frame_interval:
            continue
        last_frame_time = now_ts

        now = datetime.now()

        results = model(frame, verbose=False, conf=0.3)[0]

        # filter to vehicle classes only
        mask = np.isin(results.boxes.cls.cpu().numpy().astype(int), list(VEHICLE_CLASSES))
        boxes = results.boxes.xyxy.cpu().numpy()[mask]
        confs = results.boxes.conf.cpu().numpy()[mask]
        class_ids = results.boxes.cls.cpu().numpy().astype(int)[mask]

        detections = sv.Detections(
            xyxy=boxes,
            confidence=confs,
            class_id=class_ids,
        ) if len(boxes) > 0 else sv.Detections.empty()

        detections = tracker.update_with_detections(detections)

        # count line crossings
        for i in range(len(detections)):
            x1, y1, x2, y2 = detections.xyxy[i]
            cy = (y1 + y2) / 2
            track_id = detections.tracker_id[i] if detections.tracker_id is not None else None

            if track_id is None:
                continue

            track_key = f"{camera_id}_{track_id}"
            if cy > LINE_POSITION and track_key not in crossed_ids[camera_id]:
                crossed_ids[camera_id].add(track_key)
                active_counts[camera_id] += 1
                print(f"[{now.isoformat()}] [{camera_id}] Vehicle crossed line (count={active_counts[camera_id]})")

        # log per-minute counts
        elapsed = now - last_log_time[camera_id]
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

    cap.release()
