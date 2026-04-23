"""
DevOps Info Service
Main application module
"""

import os
import socket
import platform
import logging
import time
import threading
from datetime import datetime, timezone

from flask import Flask, jsonify, request
from prometheus_client import Counter, Histogram, Gauge, generate_latest

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 5000))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

SERVICE_NAME = "devops-info-service"
SERVICE_VERSION = "1.0.1"
SERVICE_DESCRIPTION = "DevOps course info service"
FRAMEWORK = "Flask"

# -----------------------------------------------------------------------------
# App setup
# -----------------------------------------------------------------------------
app = Flask(__name__)
START_TIME = datetime.now(timezone.utc)
VISITS_LOCK = threading.Lock()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

logger.info("Starting DevOps Info Service...")

# -----------------------------------------------------------------------------
# Prometheus Metrics
# -----------------------------------------------------------------------------
# HTTP-level RED metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

http_requests_in_progress = Gauge(
    'http_requests_in_progress',
    'HTTP requests in progress'
)

# Application-specific (business) metrics
endpoint_calls = Counter(
    'devops_info_endpoint_calls',
    'Number of calls per logical endpoint',
    ['endpoint']
)

system_info_collection_seconds = Histogram(
    'devops_info_system_collection_seconds',
    'Time spent collecting system information'
)

# -----------------------------------------------------------------------------
# Middleware for metrics
# -----------------------------------------------------------------------------
@app.before_request
def before_request():
    request.start_time = time.time()
    http_requests_in_progress.inc()


@app.after_request
def after_request(response):
    duration = time.time() - request.start_time

    http_requests_total.labels(
        method=request.method,
        endpoint=request.path,
        status=response.status_code
    ).inc()

    http_request_duration_seconds.labels(
        method=request.method,
        endpoint=request.path
    ).observe(duration)

    http_requests_in_progress.dec()

    return response

# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------
def get_uptime():
    """Return uptime in seconds and human-readable format."""
    delta = datetime.now(timezone.utc) - START_TIME
    seconds = int(delta.total_seconds())
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return {
        "seconds": seconds,
        "human": f"{hours} hours, {minutes} minutes"
    }


def get_system_info():
    """Collect system information."""
    # Measure how long it takes to collect system info
    with system_info_collection_seconds.time():
        return {
            "hostname": socket.gethostname(),
            "platform": platform.system(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "cpu_count": os.cpu_count(),
            "python_version": platform.python_version(),
        }


def get_visits_file_path():
    return os.getenv("VISITS_FILE", "/data/visits")


def read_visits():
    visits_file = get_visits_file_path()
    try:
        with open(visits_file, "r", encoding="utf-8") as file:
            raw_value = file.read().strip()
        return int(raw_value) if raw_value else 0
    except FileNotFoundError:
        return 0
    except ValueError:
        return 0


def write_visits(value):
    visits_file = get_visits_file_path()
    directory = os.path.dirname(visits_file)
    if directory:
        os.makedirs(directory, exist_ok=True)
    temp_file = f"{visits_file}.tmp"
    with open(temp_file, "w", encoding="utf-8") as file:
        file.write(str(value))
    os.replace(temp_file, visits_file)


def increment_visits():
    with VISITS_LOCK:
        current = read_visits()
        updated = current + 1
        write_visits(updated)
        return updated

# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------
@app.route("/", methods=["GET"])
def index():
    """Main endpoint providing service and system information."""
    logger.info("Handling request to /")

    # Business metric: count calls to main endpoint
    endpoint_calls.labels(endpoint="/").inc()
    visits = increment_visits()

    uptime = get_uptime()

    response = {
        "service": {
            "name": SERVICE_NAME,
            "version": SERVICE_VERSION,
            "description": SERVICE_DESCRIPTION,
            "framework": FRAMEWORK,
        },
        "system": get_system_info(),
        "runtime": {
            "uptime_seconds": uptime["seconds"],
            "uptime_human": uptime["human"],
            "current_time": datetime.now(timezone.utc).isoformat(),
            "timezone": "UTC",
        },
        "stats": {
            "visits": visits
        },
        "request": {
            "client_ip": request.remote_addr,
            "user_agent": request.headers.get("User-Agent"),
            "method": request.method,
            "path": request.path,
        },
        "endpoints": [
            {
                "path": "/",
                "method": "GET",
                "description": "Service information"
            },
            {
                "path": "/health",
                "method": "GET",
                "description": "Health check"
            },
            {
                "path": "/ready",
                "method": "GET",
                "description": "Readiness check"
            },
            {
                "path": "/metrics",
                "method": "GET",
                "description": "Prometheus metrics"
            },
            {
                "path": "/visits",
                "method": "GET",
                "description": "Current visits counter"
            }
        ]
    }

    return jsonify(response)


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    uptime = get_uptime()

    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime_seconds": uptime["seconds"],
    })


@app.route("/ready", methods=["GET"])
def ready():
    """Readiness probe: app accepts traffic once process is up."""
    return jsonify({
        "status": "ready",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


@app.route("/metrics", methods=["GET"])
def metrics():
    """Prometheus metrics endpoint."""
    return generate_latest(), 200, {'Content-Type': 'text/plain'}


@app.route("/visits", methods=["GET"])
def visits():
    """Return current visits counter."""
    endpoint_calls.labels(endpoint="/visits").inc()
    return jsonify({
        "visits": read_visits(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

# -----------------------------------------------------------------------------
# Error handlers
# -----------------------------------------------------------------------------
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Not Found",
        "message": "Endpoint does not exist"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal Server Error",
        "message": "An unexpected error occurred"
    }), 500


# -----------------------------------------------------------------------------
# Entry point
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=DEBUG)
