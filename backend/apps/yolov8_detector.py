from roboflow import Roboflow
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Connecting to roboflow, setting up project and model
rf = Roboflow(api_key = os.getenv("ROBOFLOW_API_KEY"))
project = rf.workspace("projects-qhyq6").project("vehicle_detection_yolov8-rptry")
model = project.version(2).model

# Load Image
image_path = "backend/data/images/traffic_image.png"

# Run inference
prediction = model.predict(image_path, confidence=40, overlap=30).json()

# Save annotated image
model.predict(image_path).save("output/annotated/prediction_output.jpg")
