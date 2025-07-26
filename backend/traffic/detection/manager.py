import json
import threading
from .worker import start_camera_worker

CONFIG_PATH = "backend/traffic/config/camera_configs.json"

# give each camera a thread to run inference
def launch_all_cameras():
    with open(CONFIG_PATH, "r") as f:
        cameras = json.load(f)

    threads = []
    for cam in cameras:
        t = threading.Thread(target=start_camera_worker, args=(cam["id"], cam["stream_url"]))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

if __name__ == "__main__":
    launch_all_cameras()
