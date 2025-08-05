import os
from dotenv import load_dotenv
from flask import Blueprint, jsonify
from .wmata_alerts import wmata_bus_incidents, wmata_rail_incidents

load_dotenv()

WMATA_API_KEY = os.getenv("WMATA_API_KEY")
wmata_alerts = Blueprint("wmata_alerts", __name__)

#alerts for bus incidents
@wmata_alerts.route("/alerts/bus", methods=["GET"])
def get_bus_alerts():
    try:
        data = wmata_bus_incidents(WMATA_API_KEY)
        formatted = format_incidents(data, key = "BusIncidents")
        return jsonify({"alerts": formatted}), 200
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
@wmata_alerts.route("/alerts/rail", methods=["GET"])
def get_rail_alerts():
    try:
        data = wmata_rail_incidents(WMATA_API_KEY)
        formatted = format_incidents(data, key = "Incidents")
        return jsonify({"alerts": formatted}), 200
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500

def format_incidents(data, key):
    if not data or key not in data:
        return []

    formatted = []
    for i, incident in enumerate(data[key]):
        incident_id = incident.get('IncidentID', f"{key}-{i}")
        formatted.append({
            'id': incident_id,
            'title': incident.get('IncidentType', 'Alert'),
            'summary': incident.get('Description', 'No details available'),
            'time': incident.get('DateUpdated', ''),
            'severity': determine_severity(incident)
        })

    return formatted

def determine_severity(incident):
    """Determine alert severity based on content"""
    description = incident.get('Description', '').lower()
    
    if any(word in description for word in ['emergency', 'severe', 'closure']):
        return 'critical'
    elif any(word in description for word in ['delay', 'major']):
        return 'major'
    return 'minor'