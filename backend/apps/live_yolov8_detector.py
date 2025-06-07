
import os
import time
import requests
import tempfile
from roboflow import Roboflow
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up Roboflow
rf = Roboflow(api_key=os.getenv("ROBOFLOW_API_KEY"))
project = rf.workspace("projects-qhyq6").project("vehicle_detection_yolov8-rptry")
model = project.version(4).model

# Image stream URL
IMAGE_URL = os.getenv("TRAFFIC_CAM_URL")
while True:
    try:
        # Download the image
        response = requests.get(IMAGE_URL, stream=True)
        if response.status_code == 200:
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                tmp.write(response.content)
                tmp_path = tmp.name

            # Run inference and save annotated result
            prediction = model.predict(tmp_path, confidence=40, overlap=30)
            output_path = "output/annotated/prediction_output.jpg"
            prediction.save(output_path)

            print(f"Saved annotated image to {output_path}")

            # Delete the temp file
            os.remove(tmp_path)

        else:
            print(f"Failed to fetch image: {response.status_code}")

        # Wait 1 seconds before next pull
        time.sleep(1)

    except KeyboardInterrupt:
        print("Stopped by user.")
        break

