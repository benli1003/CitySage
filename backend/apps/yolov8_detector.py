from roboflow import Roboflow
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Step 1: Authenticate with your Roboflow API key
rf = Roboflow(api_key = os.getenv("ROBOFLOW_API_KEY"))  # <-- replace with your actual API key

# Step 2: Load your project and versioned model
project = rf.workspace("projects-qhyq6").project("vehicle_detection_yolov8-rptry")
model = project.version(2).model  # adjust the version if you're using a different one

# Step 3: Local image to test
image_path = "backend/data/images/traffic_image.png" # make sure this file exists in the same folder

# Step 4: Run inference
prediction = model.predict(image_path, confidence=40, overlap=30).json()

# Step 5: Show results
print("Detections:", prediction)

# Step 6: Save annotated image
model.predict(image_path).save("output/annotated/prediction_output.jpg")
print("Annotated image saved as 'prediction_output.jpg'")
