# ============================================================
# Google Cloud Run & Docker Optimized for FastAPI Inference
# ============================================================
FROM python:3.11-slim

# Mencegah Python menulis file .pyc dan memastikan log unbuffered
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

# Install system dependencies (curl untuk healthcheck probe)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Salin dependencies: fleksibel untuk context root maupun context web/backend
COPY requirements.txt* web/backend/requirements.txt* ./
RUN if [ -f "web/backend/requirements.txt" ]; then mv web/backend/requirements.txt requirements.txt; fi && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Salin source code dan artefak model/data
COPY . /tmp/build_context

RUN if [ -d "/tmp/build_context/web/backend" ]; then \
        # Context adalah Root Repository (docker build -f web/backend/Dockerfile .)
        cp -r /tmp/build_context/web/backend/* /app/ && \
        mkdir -p /app/artifact/model /app/artifact/data && \
        if [ -d "/tmp/build_context/artifact/model" ]; then cp -r /tmp/build_context/artifact/model/* /app/artifact/model/ 2>/dev/null || true; fi && \
        if [ -d "/tmp/build_context/artifact/data" ]; then cp -r /tmp/build_context/artifact/data/* /app/artifact/data/ 2>/dev/null || true; fi; \
    else \
        # Context adalah web/backend (cd web/backend && docker build .)
        cp -r /tmp/build_context/* /app/ && \
        mkdir -p /app/artifact/model /app/artifact/data; \
    fi && \
    rm -rf /tmp/build_context

# Expose port container (Google Cloud Run default: 8080)
EXPOSE 8080

# Healthcheck probe Docker container
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Jalankan Uvicorn dengan bind ke 0.0.0.0 dan port dinamis dari Google Cloud Run ($PORT)
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT}
