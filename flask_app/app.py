import time
import random
import logging
from flask import Flask, Response, jsonify

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
    return "IO bound task finish!"

@app.route("/cpu_task")
def cpu_task():
    for i in range(10000):
        n = i * i * i
    return "CPU bound task finish!"

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

if __name__ != '__main__':
    # Use gunicorn's logger to replace flask's default logger
    gunicorn_logger = logging.getLogger('gunicorn.error')
    # Add gunicorn's handlers to Flask's logger to ensure logs are not overridden
    if not app.logger.hasHandlers():
        app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
