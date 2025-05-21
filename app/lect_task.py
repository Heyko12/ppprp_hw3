from flask import Flask, request, jsonify, Response
import json
import os
import time
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

REQUEST_COUNT = Counter('flask_requests_total', 'Общее число HTTP запросов', ['endpoint', 'method'])
LOG_SUCCESS = Counter('flask_log_success_total', 'Успешные попытки логирования')
LOG_FAILURE = Counter('flask_log_failure_total', 'Неуспешные попытки логирования')
REQUEST_LATENCY = Histogram('flask_request_duration_seconds', 'Время обработки запроса')

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

def track(endpoint):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            start = time.time()
            REQUEST_COUNT.labels(endpoint=endpoint, method=request.method).inc()
            try:
                resp = fn(*args, **kwargs)
                duration = time.time() - start
                REQUEST_LATENCY.observe(duration)
                return resp
            except Exception:
                REQUEST_LATENCY.observe(time.time() - start)
                raise
        wrapper.__name__ = fn.__name__
        return wrapper
    return decorator

@app.route("/", methods=["GET"])
@track('home')
def home():
    return config["hello_message"]

@app.route("/status", methods=["GET"])
@track('status')
def status():
    return jsonify({"status": "ok"})

@app.route("/log", methods=["POST"])
@track('log')
def log_message():
    data = request.get_json()
    message = data.get("message")
    
    if message:
        with open(log_file_path, "a") as log_file:
            log_file.write(message + "\n")
        LOG_SUCCESS.inc()
        response = jsonify({"message": "Log saved successfully"}), 201
    else:
        LOG_FAILURE.inc()
        response = jsonify({"error": "Message is required"}), 400
    return response

@app.route("/logs", methods=["GET"])
@track('logs')
def get_logs():
    if os.path.exists(log_file_path):
        with open(log_file_path, "r") as log_file:
            logs = log_file.read()
        return logs if logs else "No logs found."
    else:
        return "Log file does not exist.", 404

@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)