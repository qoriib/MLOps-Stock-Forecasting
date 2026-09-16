# MLOps Stock Forecasting Inference Backend (FastAPI)

Backend inferensi machine learning berbasis **Python FastAPI** yang melayani peramalan harga saham time-series (ARIMA & SARIMA) dan dirancang untuk di-deploy ke **Google Cloud Run**.

---

## Fitur Utama
- **Model Loading & In-Memory Caching**: Memuat model pickled (`.pkl`) secara efisien.
- **Prediksi Probabilistik**: Menghasilkan nilai prediksi beserta rentang keyakinan 95% (`lower_bound` & `upper_bound`).
- **Penjadwalan Tanggal Hari Kerja**: Otomatis menghasilkan tanggal masa depan (Business Days) setelah tanggal historis terakhir.
- **RESTful Endpoints (Sederhana & Efisien)**:
  - `GET /` - Dokumentasi Interaktif API (Swagger UI langsung di root).
  - `GET /openapi.json` - Spesifikasi OpenAPI 3.1 schema JSON.
  - `GET /api/models` - Endpoint terpadu: daftar ticker aktif dan metadata lengkap model.
  - `POST /api/predict` - Inferensi model peramalan (JSON payload: `{"ticker": "BBCA.JK", "steps": 30}`).
  - `GET /api/stocks/{ticker}` - Data historis harga saham untuk visualisasi chart.

---

## Struktur Direktori Modular
Aplikasi backend telah dimodularisasi dengan arsitektur berlapis:
```text
web/backend/
├── app/
│   ├── core/            # Konfigurasi aplikasi & path discovery (MODEL_DIR, DATA_DIR)
│   ├── schemas/         # Skema validasi Pydantic (request & response)
│   ├── services/        # Logika bisnis (pemuatan model, forecasting, data historis)
│   └── api/             # Routing FastAPI (models, predict, stocks)
├── main.py              # Entrypoint aplikasi FastAPI & Uvicorn runner
├── pyproject.toml       # Definisi dependensi & metadata package Poetry
├── poetry.lock          # Versi lock dependensi Python
├── Dockerfile           # Konfigurasi container untuk Google Cloud Run
└── README.md
```

---

## 1. Menjalankan Secara Lokal

Direktori backend mendukung manajemen dependensi modern menggunakan **Poetry** (`pyproject.toml` & `poetry.lock`):

```bash
# Masuk ke direktori backend
cd web/backend

# Install dependencies dari lockfile
poetry install

# Jalankan server
poetry run python main.py
# atau menggunakan Uvicorn reload:
poetry run uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

Akses dokumentasi interaktif langsung di: [http://localhost:8080/](http://localhost:8080/)
Akses skema OpenAPI di: [http://localhost:8080/openapi.json](http://localhost:8080/openapi.json)

---

## 2. Menjalankan dengan Docker Secara Lokal

### Menggunakan Docker Compose (Direkomendasikan)
Dari direktori root proyek (`MLOps-Stock-Forecasting`):
```bash
# Build dan jalankan container di latar belakang
docker compose up --build -d

# Cek log aplikasi
docker compose logs -f

# Hentikan container
docker compose down
```

### Menggunakan Docker CLI Standar
```bash
# Build Docker image dari root proyek
docker build -t stock-api -f web/backend/Dockerfile .

# Jalankan container
docker run -p 8080:8080 -e PORT=8080 stock-api
```

---

## 3. Panduan Deploy ke Google Cloud Run

### Persiapan:
1. Pastikan Google Cloud SDK (`gcloud`) telah terpasang dan login:
   ```bash
   gcloud auth login
   gcloud config set project mlops-stock-forecast
   ```
2. Aktifkan API Cloud Run & Artifact Registry:
   ```bash
   gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com
   ```

### Deploy Langsung (Source-based Deploy):
Jalankan perintah ini dari direktori root proyek:
```bash
gcloud run deploy stock-forecast-api \
  --source . \
  --dockerfile web/backend/Dockerfile \
  --platform managed \
  --region asia-southeast2 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 1 \
  --timeout 300
```

Setelah selesai, Google Cloud Run akan memberikan URL HTTPS publik layanan Anda (contoh: `https://stock-forecast-api-xxxxx-as.a.run.app`).
