import os

port_string = os.getenv("PORT", "8000")
bind = f"0.0.0.0:{port_string}"

worker_count_string = os.getenv("WEB_CONCURRENCY", "2")
workers = int(worker_count_string)

worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
keepalive = 5
accesslog = "-"
errorlog = "-"
