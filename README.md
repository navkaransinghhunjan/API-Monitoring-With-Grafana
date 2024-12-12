# Flask Monitoring with Prometheus, StatsD, and Custom Metrics

This project provides a Flask-based web application that monitors performance metrics of its endpoints using Prometheus and StatsD. It tracks request durations, counts, and status codes, and exposes these metrics through a custom ```/stats``` endpoint for easy integration with monitoring systems like Prometheus and Grafana.

## Features
* Custom API Monitoring: Monitors key performance metrics such as average request duration, request count, and HTTP status code distribution.
* Prometheus Integration: Queries Prometheus to gather real-time performance data for each endpoint in the Flask application.
* Error Handling: Logs unhandled exceptions and provides custom error responses.
StatsD Integration: Tracks API request performance and sends metrics to a StatsD server for real-time monitoring.
* Logging: Logs application events and errors to a file for further analysis and debugging.
* Metrics Visualization: The metrics can be visualized using Prometheus and Grafana, allowing you to monitor the health of your API in real-time.
* Node Exporter: Monitors system-level metrics, such as CPU, memory, and disk usage, providing insights into server health.
* Authentication Support:
    1. Azure AD: Enables secure authentication through Azure Active Directory.
    2. Google OAuth: Allows users to log in using their Google accounts.

## Directory Structure

```plaintext
flask-monitoring/
├── etc/
│   ├── dashboards/              # Placeholder for Grafana dashboards
|   |   └── dashboards.yaml      # Dashboard json file
│   ├── grafana/                 # Grafana setup files
│   │   └── datasource.yml       # Data source configuration
│   ├── loki/
|   |   └── loki-config.yml           # Loki configuration files
│   ├── prometheus/              # Prometheus configuration files
│   │   └── prometheus.yml       # Prometheus scrape jobs
│   └── promtail/                # Promtail configuration files
│       └── config.yml           # Promtail log scraping configuration
├── flask_app/
│   ├── logs/                    # Log directory for the Flask app
│   ├── app.py                   # Flask application code
│   ├── Dockerfile               # Dockerfile for Flask app
│   ├── requirements.txt         # Python dependencies
│   └── utils.py                 # Custom StatsD middleware and settings
├── docker-compose.yml           # Docker Compose configuration
├── README.md                    # Project documentation
└── request-script.sh            # Bash script for testing API requests
```
## Setup Instructions

1. **Clone the Repository**

```bash
git clone https://github.com/navkaransinghhunjan/API-Logs-And-Metrics-Monitoring-With-Grafana.git
cd flask-monitoring
```

2. **Build and Run the Project**

```bash
docker-compose up --build
```
3. **Access Services**

Flask Application: ```http://localhost:8000```

Prometheus: ```http://localhost:9090```

Grafana: ```http://localhost:3000```

Default Grafana credentials:
Username: admin
Password: admin

4. **Testing the Flask Application**

Run the API testing script:
```bash
bash request-script.sh
```

5. **Metrics and Logs**

Metrics (via StatsD) and Logs generated by the Flask app are visible in Grafana.

## Endpoints
* /: A simple health check endpoint.

* /io_task: Simulates an I/O-bound task.

* /cpu_task: Simulates a CPU-bound task.

* /random_sleep: Sleeps for a random time (0-5 seconds) and optionally raises a simulated error.

* /random_status: Returns a random HTTP status code (200, 300, 400, or 500).

* /stats/<app_name>/<endpoint>: Returns performance metrics for a given app and endpoint. Example:

```
curl http://127.0.0.1:8000/stats/flask-monitoring/cpu_task
```