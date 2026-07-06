import json
import os
import time
import logging

from .worker import start_camera_worker, stop_camera_worker, start_flusher

logger = logging.getLogger(__name__)

CONFIG_PATH = os.path.join(
    os.path.dirname(__file__),
    os.pardir,
    "config",
    "camera_configs.json"
)

# Round-robin scheduling: instead of running all cameras concurrently 24/7
# (the dominant EC2 cost), only CONCURRENT_CAMERAS run inference at a time,
# each active window lasting ACTIVE_WINDOW_SECONDS before cycling to the next
# group. Tune these via env without code changes.
CONCURRENT_CAMERAS = int(os.getenv("CONCURRENT_CAMERAS", "3"))
ACTIVE_WINDOW_SECONDS = int(os.getenv("ACTIVE_WINDOW_SECONDS", "120"))
# Small stagger between starting cameras in a group to spread decode/init load.
START_STAGGER_SECONDS = int(os.getenv("START_STAGGER_SECONDS", "2"))


def _load_cameras():
    with open(CONFIG_PATH, "r") as file:
        return json.load(file)


def launch_all_cameras():
    """
    Run traffic detection using a round-robin scheduler.

    Only CONCURRENT_CAMERAS pipelines run at once. Each group runs for
    ACTIVE_WINDOW_SECONDS, then is stopped and the next group starts. Counts
    for observed minutes are buffered and flushed by the background flusher.
    """
    cameras = _load_cameras()
    if not cameras:
        logger.warning("no cameras configured")
        return

    n = len(cameras)
    concurrent = max(1, min(CONCURRENT_CAMERAS, n))
    logger.info(
        "starting round-robin detection: %d cameras, %d concurrent, %ds/window",
        n, concurrent, ACTIVE_WINDOW_SECONDS,
    )

    # start the background DB batch-flush thread once
    start_flusher()

    idx = 0
    while True:
        # select the next group of cameras (wraps around the list)
        group = [cameras[(idx + j) % n] for j in range(concurrent)]
        idx = (idx + concurrent) % n

        running = []  # (cam_id, pipeline)
        for cam in group:
            cam_id = cam.get("id")
            stream_url = cam.get("logging_url")
            pipeline = start_camera_worker(cam_id, stream_url)
            running.append((cam_id, pipeline))
            if START_STAGGER_SECONDS:
                time.sleep(START_STAGGER_SECONDS)

        # let the group observe for its active window (minus the stagger already spent)
        observed = START_STAGGER_SECONDS * len(running)
        remaining = max(0, ACTIVE_WINDOW_SECONDS - observed)
        time.sleep(remaining)

        # stop the group before cycling to the next
        for cam_id, pipeline in running:
            stop_camera_worker(cam_id, pipeline)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    launch_all_cameras()
