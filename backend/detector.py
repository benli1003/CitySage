import cv2
from inference import InferencePipeline
from inference.core.interfaces.stream.sinks import render_boxes
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("ROBOFLOW_API_KEY")

# Initialize the pipeline with your custom model
pipeline = InferencePipeline.init(
    model_id="vehicle_detection_yolov8-rptry/4",
    api_key=api_key,
    video_reference="https://strmr5.sha.maryland.gov/rtplive/8c00118a004b00a0004e3536c4235c0a/chunklist_w188272287.m3u8",
    on_prediction=render_boxes,
    confidence=0.3,
    max_fps=10,
)

# Start real-time inference
pipeline.start()
