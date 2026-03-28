#!/usr/bin/env python3
"""
Hays Edinburgh AWS DevOps POC — Application
A simple Python web application demonstrating AWS DevOps best practices.
Designed for deployment on EKS with Helm.
"""

import json
import logging
import os
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Dict, Any
from urllib.parse import urlparse

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp":"%(asctime)s","level":"%(levelname)s","message":"%(message)s","logger":"%(name)s"}',
    datefmt="%Y-%m-%dT%H:%M:%SZ",
)
logger = logging.getLogger("hays-devops-app")

# Application configuration
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
APP_NAME = "hays-devops-app"
ENVIRONMENT = os.getenv("ENV", "development")
PORT = int(os.getenv("PORT", "8080"))
HOST = os.getenv("HOST", "0.0.0.0")

# Metrics counters (in-memory, would use Prometheus client in production)
_metrics: Dict[str, Any] = {
    "requests_total": 0,
    "requests_5xx": 0,
    "requests_4xx": 0,
    "start_time": time.time(),
}


def get_health_status() -> Dict[str, Any]:
    """Return application health status."""
    return {
        "status": "healthy",
        "version": APP_VERSION,
        "environment": ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "uptime_seconds": round(time.time() - _metrics["start_time"], 2),
    }


def get_readiness_status() -> Dict[str, Any]:
    """Return application readiness status."""
    # Check dependencies here in production (DB connections, etc.)
    return {
        "status": "ready",
        "version": APP_VERSION,
        "environment": ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "checks": {
            "database": "ok",
            "cache": "ok",
            "external_api": "ok",
        },
    }


def get_metrics() -> str:
    """Return Prometheus-format metrics."""
    uptime = round(time.time() - _metrics["start_time"], 2)
    lines = [
        "# HELP hays_app_requests_total Total number of HTTP requests",
        "# TYPE hays_app_requests_total counter",
        f"hays_app_requests_total {_metrics['requests_total']}",
        "# HELP hays_app_errors_4xx_total Total 4xx errors",
        "# TYPE hays_app_errors_4xx_total counter",
        f"hays_app_errors_4xx_total {_metrics['requests_4xx']}",
        "# HELP hays_app_errors_5xx_total Total 5xx errors",
        "# TYPE hays_app_errors_5xx_total counter",
        f"hays_app_errors_5xx_total {_metrics['requests_5xx']}",
        "# HELP hays_app_uptime_seconds Application uptime in seconds",
        "# TYPE hays_app_uptime_seconds gauge",
        f"hays_app_uptime_seconds {uptime}",
        f'hays_app_info{{version="{APP_VERSION}",environment="{ENVIRONMENT}"}} 1',
    ]
    return "\n".join(lines) + "\n"


def get_app_info() -> Dict[str, Any]:
    """Return application information."""
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "environment": ENVIRONMENT,
        "description": "Hays Edinburgh AWS DevOps POC — demonstrating EKS, Terraform, CI/CD, and observability",
        "github": "https://github.com/saikirangvariganti/hays-edinburgh-aws-devops-poc",
        "features": [
            "Kubernetes/EKS deployment with Helm",
            "Terraform IaC for VPC, EKS, RDS, S3",
            "Jenkins + GitHub Actions CI/CD pipelines",
            "IAM least-privilege + KMS encryption",
            "CloudWatch + Prometheus/Grafana observability",
            "On-prem to AWS migration assessment",
        ],
        "endpoints": {
            "GET /": "Application info",
            "GET /health": "Liveness probe",
            "GET /ready": "Readiness probe",
            "GET /metrics": "Prometheus metrics",
            "GET /api/v1/status": "API status",
        },
    }


class RequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the POC application."""

    def log_message(self, format_str, *args):
        """Override default logging to use structured format."""
        logger.info(
            "method=%s path=%s status=%s",
            self.command,
            self.path,
            args[1] if len(args) > 1 else "-",
        )

    def send_json_response(self, status_code: int, data: Any):
        """Send a JSON response."""
        _metrics["requests_total"] += 1
        if status_code >= 500:
            _metrics["requests_5xx"] += 1
        elif status_code >= 400:
            _metrics["requests_4xx"] += 1

        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.send_header("X-App-Version", APP_VERSION)
        self.send_header("X-Environment", ENVIRONMENT)
        self.end_headers()
        self.wfile.write(body)

    def send_text_response(self, status_code: int, content: str):
        """Send a plain text response."""
        _metrics["requests_total"] += 1
        body = content.encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"

        if path == "/":
            self.send_json_response(200, get_app_info())
        elif path == "/health":
            self.send_json_response(200, get_health_status())
        elif path == "/ready":
            self.send_json_response(200, get_readiness_status())
        elif path == "/metrics":
            self.send_text_response(200, get_metrics())
        elif path == "/api/v1/status":
            self.send_json_response(200, {
                "status": "operational",
                "version": APP_VERSION,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            })
        else:
            self.send_json_response(404, {
                "error": "Not Found",
                "path": self.path,
                "available_endpoints": list(get_app_info()["endpoints"].keys()),
            })


def run_server(host: str = HOST, port: int = PORT):
    """Start the HTTP server."""
    server = HTTPServer((host, port), RequestHandler)
    logger.info("Starting %s v%s on %s:%d (env: %s)", APP_NAME, APP_VERSION, host, port, ENVIRONMENT)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
        server.shutdown()


if __name__ == "__main__":
    run_server()
