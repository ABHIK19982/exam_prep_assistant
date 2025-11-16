"""
Gunicorn configuration file for production deployment.
This file contains production-ready settings for the WSGI application.
"""
import os
import multiprocessing

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', '10000')}"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 5

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = os.environ.get("LOG_LEVEL", "info").lower()

# Process naming
proc_name = "cvproject-exam-prep-assistant"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (uncomment and configure if using HTTPS)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Preload app for better performance
preload_app = True

# Worker timeout for graceful shutdown
graceful_timeout = 30

# Enable stats server (optional, for monitoring)
# statsd_host = None
# statsd_prefix = "gunicorn"
