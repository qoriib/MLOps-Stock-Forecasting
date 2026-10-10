import multiprocessing
import os

port_string = os.getenv("PORT", "8000")
bind = f"0.0.0.0:{port_string}"

# 4 workers optimal memanfaatkan 4 CPU Cores dan 8 GiB RAM container (~1.4 GB / 8 GB RAM)
default_workers = int(os.getenv("WEB_CONCURRENCY", "4"))
workers = default_workers

worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
backlog = 2048
timeout = 120
keepalive = 65
graceful_timeout = 30

max_requests = 10000
max_requests_jitter = 500

accesslog = "-"
errorlog = "-"
loglevel = os.getenv("LOG_LEVEL", "info")
