from flask import Flask, request, jsonify
import json
import os
import time
from prometheus_client import make_wsgi_app, Counter, Histogram
from werkzeug.middleware.dispatcher import DispatcherMiddleware

app = Flask(__name__)

LOG_REQUEST_COUNTER = Counter('app_log_requests_total', 'Total number of /log requests')
LOG_REQUEST_SUCCESS = Counter('app_log_requests_success', 'Total successful log requests', ['status'])
LOG_REQUEST_DURATION = Histogram('app_log_request_duration_seconds', 'Duration of /log requests')

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {'/metrics': make_wsgi_app()})

log_file_path = "logs/app.log"

CONFIG_PATH = "/app/config/app-config.json"

def load_config():
    try:
        with open(CONFIG_PATH) as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return {"hello_message": "Welcome to the default app"}
    
config = load_config()

@app.route("/", methods=["GET"])
def home():
    return config["hello_message"]

@app.route("/status", methods=["GET"])
def status():
    return jsonify({"status": "ok"})

@app.route("/log", methods=["POST"])
def log_message():
    start_time = time.time()
    LOG_REQUEST_COUNTER.inc()
    data = request.get_json()
    message = data.get("message")
    
    try:
        if message:
            with open(log_file_path, "a") as log_file:
                log_file.write(message + "\n")
            LOG_REQUEST_SUCCESS.labels(status='success').inc()
            response = jsonify({"message": "Log saved successfully"}), 201
        else:
            LOG_REQUEST_SUCCESS.labels(status='error').inc()
            response = jsonify({"error": "Message is required"}), 400
    except Exception as e:
        LOG_REQUEST_SUCCESS.labels(status='error').inc()
        response = jsonify({"error": str(e)}), 500
    finally:
        duration = time.time() - start_time
        LOG_REQUEST_DURATION.observe(duration)
    
    return response

@app.route("/logs", methods=["GET"])
def get_logs():
    if os.path.exists(log_file_path):
        with open(log_file_path, "r") as log_file:
            logs = log_file.read()
        return logs if logs else "No logs found."
    else:
        return "Log file does not exist.", 404

if __name__ == "__main__":
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)