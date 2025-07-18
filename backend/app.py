from flask import Flask, render_template, Response
from flask_cors import CORS
# from traffic.traffic_detector import generate_frames

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])
from scrapers.alert_routes import alerts  # Import your blueprint
app.register_blueprint(alerts, url_prefix='/api')

@app.route('/')
def index():
    return render_template('index.html')  # loads templates/index.html

#@app.route('/video')
#def video():
#    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

print("\nRegistered routes:")
for rule in app.url_map.iter_rules():
    print(f"{rule.endpoint}: {rule}")


@app.route('/ping')
def ping():
    return "pong"

if __name__ == '__main__':
    app.run(debug=True, port=5050)
