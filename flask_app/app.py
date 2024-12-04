import time
import random
import logging
import requests  # Import requests
from flask import Flask, Response, jsonify
from prometheus_client import CollectorRegistry, generate_latest, Gauge
from utils import setting_statsd, StatsdMiddleware

app = Flask(__name__)

# Setting statsd host and port
setting_statsd()
# Add statsd middleware to track each request and send statsd UDP request
app.wsgi_app = StatsdMiddleware(app.wsgi_app, "flask-monitoring")

# Configure logging to write to a file
log_handler = logging.FileHandler('/var/log/flask/app.log')
log_handler.setLevel(logging.DEBUG)
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler.setFormatter(log_formatter)

# Add the handler to the app logger
app.logger.addHandler(log_handler)
app.logger.setLevel(logging.DEBUG)

# Error handler for unhandled exceptions
@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.exception("Unhandled Exception occurred!")
    return jsonify({"error": "Internal Server Error"}), 500

@app.route("/")
def hello_world():
    app.logger.error("Hello, World!")
    return "Hello, World!"

@app.route("/io_task")
def io_task():
    time.sleep(2)
    return "IO bound task finished!"

@app.route("/cpu_task")
def cpu_task():
    for i in range(10000):
        n = i * i * i
    return "CPU bound task finished!"

@app.route("/random_sleep")
def random_sleep():
    try:
        time.sleep(random.randint(0, 5))
        raise ValueError("Demo Error!")  # Simulated error for testing
    except Exception as e:
        app.logger.exception("Error in /random_sleep endpoint")
        return jsonify({"error": str(e)}), 500

@app.route("/random_status")
def random_status():
    status_code = random.choice([200] * 6 + [300, 400, 400, 500])
    if status_code >= 400:
        app.logger.error(f"Random status code generated: {status_code}")
    return Response("random status", status=status_code)

@app.route("/stats/<app_name>/<endpoint>")
def get_endpoint_stats(app_name, endpoint):
    try:
        prometheus_url = "http://prometheus:9090"
        
        # Queries
        avg_duration_query = (
            f'flask_request_duration_seconds_sum{{app_name="{app_name}", endpoint="/{endpoint}"}} / '
            f'flask_request_duration_seconds_count{{app_name="{app_name}", endpoint="/{endpoint}"}}'
        )
        request_count_query = f'flask_request_duration_seconds_count{{endpoint="/{endpoint}", app_name="{app_name}"}}'
        percentage_200_query = (
            f'sum by(endpoint, method) (flask_request_status_total{{app_name="{app_name}", status="200", endpoint="/{endpoint}"}}) / '
            f'sum by(endpoint, method) (flask_request_status_total{{app_name="{app_name}", endpoint="/{endpoint}"}})'
        )

        # Fetch average duration
        duration_response = requests.get(f"{prometheus_url}/api/v1/query", params={"query": avg_duration_query})
        duration_data = duration_response.json()
        avg_duration = duration_data["data"]["result"][0]["value"][1] if duration_data["data"]["result"] else None

        # Fetch total request count for the endpoint
        count_response = requests.get(f"{prometheus_url}/api/v1/query", params={"query": request_count_query})
        count_data = count_response.json()
        request_count = count_data["data"]["result"][0]["value"][1] if count_data["data"]["result"] else None

        # Fetch 200 OK request percentage
        percentage_response = requests.get(f"{prometheus_url}/api/v1/query", params={"query": percentage_200_query})
        percentage_data = percentage_response.json()
        percentage_200 = percentage_data["data"]["result"][0]["value"][1] if percentage_data["data"]["result"] else None

        # Return results
        return jsonify({
            "app_name": app_name,
            "endpoint": endpoint,
            "metrics": {
                "avg_request_duration": avg_duration,
                "request_count": request_count,
                "percentage_200": percentage_200,
            }
        })
    except Exception as e:
        app.logger.exception("Error in /stats endpoint")
        return jsonify({"error": str(e)}), 500

if __name__ != '__main__':
    # Use gunicorn's logger to replace flask's default logger
    gunicorn_logger = logging.getLogger('gunicorn.error')
    # Add gunicorn's handlers to Flask's logger to ensure logs are not overridden
    if not app.logger.hasHandlers():
        app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
