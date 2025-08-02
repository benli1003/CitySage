from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from .database_summary import get_counts, generate_summary

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

    end = datetime.now()
    start = end - timedelta(hours=hours)

    # fetch and format stats
    raw = get_counts(start, end)
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
            "hours": hours
        }
    })
    