"""Gunicorn configuration for EDA Agent Flask app."""

import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', 8000)}"
backlog = 2048

# Worker processes
workers = int(os.environ.get('GUNICORN_WORKERS', 2))
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 100

# Preload app for better performance
preload_app = True

# Logging
errorlog = "-"  # stderr
loglevel = os.environ.get('GUNICORN_LOG_LEVEL', 'info')
accesslog = "-"  # stdout
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = 'eda-agent'

# Server mechanics
daemon = False
pidfile = None
tmp_upload_dir = None
