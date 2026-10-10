import multiprocessing
import os

port_string = os.getenv("PORT", "8000")
bind = f"0.0.0.0:{port_string}"

default_workers = max(2, min(multiprocessing.cpu_count(), 4))
worker_count_string = os.getenv("WEB_CONCURRENCY", str(default_workers))
workers = int(worker_count_string)

worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
backlog = 2048
timeout = 120
keepalive = 65

max_requests = 10000
max_requests_jitter = 500

accesslog = "-"
errorlog = "-"
loglevel = os.getenv("LOG_LEVEL", "info")
