import json
import threading
import os
import time
from .worker import start_camera_worker

CONFIG_PATH = os.path.join(
    os.path.dirname(__file__),
    os.pardir,
    "config",
    "camera_configs.json"
)

def launch_all_cameras():
    with open(CONFIG_PATH, "r") as file:
        cameras = json.load(file)
        
    print(f"Starting traffic detection for {len(cameras)} cameras...")
    
    threads = []
    for i, cam in enumerate(cameras):
        cam_id = cam.get("id")
        logging_url = cam.get("logging_url")
        
        print(f"Initializing camera {i+1}/{len(cameras)}: {cam_id}")
        
        t = threading.Thread(
            target = start_camera_worker,
            args = (cam_id, logging_url),
            daemon = True
        )
        t.start()
        threads.append(t)
        
        if i < len(cameras) - 1:
            time.sleep(5)
    
    print("All cameras initialized. Traffic detection active.")
    
    for t in threads:
        t.join()

if __name__ == "__main__":
    launch_all_cameras()
