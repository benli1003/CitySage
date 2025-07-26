from flask import Flask, render_template, Response
from flask_cors import CORS
from traffic.detection.manager import launch_all_cameras

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])
from scrapers.alert_routes import alerts
app.register_blueprint(alerts, url_prefix='/api')

print("\nRegistered routes:")
for rule in app.url_map.iter_rules():
    print(f"{rule.endpoint}: {rule}")

if __name__ == '__main__':
    launch_all_cameras()
    app.run(debug=True, port=5050)
