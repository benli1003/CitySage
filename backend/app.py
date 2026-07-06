import os
import threading
from flask import Flask
from flask_cors import CORS

from backend.traffic.detection.manager import launch_all_cameras
from backend.scrapers.alert_routes import wmata_alerts
from backend.traffic.detection.traffic_routes import traffic

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# register blueprints under /api
app.register_blueprint(wmata_alerts, url_prefix="/api")
app.register_blueprint(traffic, url_prefix="/api")

if __name__ == "__main__":
    # start camera inference in background
    threading.Thread(target=launch_all_cameras, daemon=True).start()

    # run Flask. Debug is off by default; enable locally with FLASK_DEBUG=1.
    # Never enable debug in production: it exposes the Werkzeug debugger,
    # which allows remote code execution on a reachable host.
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=5050, debug=debug)
