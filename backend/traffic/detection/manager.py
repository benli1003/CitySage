import json
import threading
import os
from .worker import start_camera_worker

# path to camera configs
CONFIG_PATH = os.path.join(
    os.path.dirname(__file__),
    os.pardir,
    "config",
    "camera_configs.json"
)

def launch_all_cameras():
    with open(CONFIG_PATH, "r") as file:
        cameras = json.load(file)
        
    threads = [] #store running threads
    for cam in cameras:
        cam_id = cam.get("id")
        stream_url = cam.get("stream_url")
        
        # set up thread for each camera, start it, and add to list
        t = threading.Thread(
            target = start_camera_worker,
            args = (cam_id, stream_url),
            daemon = True
        )
        t.start()
        threads.append(t)

    # continously run threads
    for t in threads:
        t.join()

if __name__ == "__main__":
    launch_all_cameras()
