from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from .database_summary import get_counts, generate_summary
import json
import os

traffic = Blueprint("traffic", __name__)

# traffic summary for the last hour or whatever user specifies
@traffic.route("/traffic-summary", methods = ["GET"])
def traffic_summary():
    # validate hours
    hours_str = request.args.get("hours", "1")
    try:
        hours = int(hours_str)
    except ValueError:
        return jsonify({"error": "Invalid 'hours' parameter"}), 400
    
    # parse for specific camera     
    camera_id = request.args.get("camera_id")

    end = datetime.now()
    start = end - timedelta(hours=hours)

    # fetch and format stats
    raw = get_counts(start, end)
    
    # filter for specific camera
    if camera_id:
        raw = [r for r in raw if r[0] == camera_id]
        
    stats = [
        {"camera_id": cam, "events": ev, "avg_per_min": float(avg)}
        for cam, ev, avg in raw
    ]

    # get summary
    summary = generate_summary(raw, start, end)

    return jsonify({
        "summary": summary,
        "stats": stats,
        "period": {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "hours": hours,
            "camera": camera_id
        }
    })

# camera configurations endpoint
@traffic.route("/cameras", methods=["GET"])
def get_cameras():
    try:
        config_path = os.path.join(os.path.dirname(__file__), "..", "config", "camera_configs.json")
        with open(config_path, "r") as f:
            cameras = json.load(f)
        return jsonify({"cameras": cameras})
    except FileNotFoundError:
        return jsonify({"error": "Camera configuration not found"}), 404
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid camera configuration"}), 500
    