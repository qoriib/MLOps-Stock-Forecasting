# ============================================================
# Google Cloud Run Optimized Dockerfile for FastAPI Inference
# ============================================================
FROM python:3.11-slim

# Mencegah Python menulis file .pyc dan memastikan output log unbuffered
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

# Install system dependencies jika diperlukan
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Salin source code backend
COPY . /app

# Salin artefak model dan data (jika build context dari root atau backend)
# Pastikan direktori artefak tersedia
RUN mkdir -p /app/artifact/model /app/artifact/data

# Expose port container (Google Cloud Run default: 8080)
EXPOSE 8080

# Jalankan Uvicorn dengan bind ke 0.0.0.0 dan port dinamis dari Google Cloud Run ($PORT)
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT}
