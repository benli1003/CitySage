import os
from dotenv import load_dotenv
from flask import Blueprint, jsonify
from flask_cors import CORS
from .wmata_alerts import wmata_bus_incidents, wmata_rail_incidents

alerts = Blueprint("alerts", __name__)
load_dotenv()
WMATA_API_KEY = os.getenv("WMATA_API_KEY")

#alerts for bus incidents
@alerts.route("/alerts/bus", methods=["GET"])
def get_wmata_alerts():
    try:
        data = wmata_bus_incidents(WMATA_API_KEY)
        formatted = format_incidents(data, key = "BusIncidents")
        return jsonify({"alerts": formatted}), 200
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
@alerts.route("/alerts/rail", methods=["GET"])
def get_rail_alerts():
    try:
        data = wmata_rail_incidents(WMATA_API_KEY)
        formatted = format_incidents(data, key = "RailIncidents")
        return jsonify({"alerts": formatted}), 200
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500

    


def format_incidents(data, key):
    if not data or key not in data:
        return []

    formatted = []
    for incident in data[key]:
        formatted.append({
            'title': incident.get('IncidentType', 'Alert'),
            'summary': incident.get('Description', 'No details available'),
            'time': incident.get('DateUpdated', '')
        })

    return formatted


@alerts.route("/test", methods=["GET"])
def test_endpoint():
    return jsonify({"status": "working"}), 200