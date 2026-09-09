# MLOps Stock Forecasting Inference Backend (FastAPI)

Backend inferensi machine learning berbasis **Python FastAPI** yang melayani peramalan harga saham time-series (ARIMA & SARIMA) dan dirancang untuk di-deploy ke **Google Cloud Run**.

---

## Fitur Utama
- **Model Loading & In-Memory Caching**: Memuat model pickled (`.pkl`) secara efisien.
- **Prediksi Probabilistik**: Menghasilkan nilai prediksi beserta rentang keyakinan 95% (`lower_bound` & `upper_bound`).
- **Penjadwalan Tanggal Hari Kerja**: Otomatis menghasilkan tanggal masa depan (Business Days) setelah tanggal historis terakhir.
- **RESTful Endpoints**:
  - `GET /` - Informasi layanan dan navigasi endpoint.
  - `GET /health` - Healthcheck probe untuk Cloud Run.
  - `GET /api/models` - Daftar model yang tersedia.
  - `POST /api/predict` - Inferensi model (JSON payload: `{"ticker": "BBCA.JK", "steps": 30}`).
  - `GET /api/predict/{ticker}` - Convenience GET endpoint inferensi (`/api/predict/BBCA.JK?steps=30`).
  - `GET /api/stocks/{ticker}` - Data historis harga saham untuk visualisasi chart.
  - `GET /docs` - Dokumentasi interaktif OpenAPI / Swagger UI.

---

## 1. Menjalankan Secara Lokal

### A. Menggunakan Python Virtual Environment
```bash
# Masuk ke direktori backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Jalankan server
python main.py
# atau:
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Akses dokumentasi Swagger UI di: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 2. Menjalankan dengan Docker Secara Lokal

```bash
# Build Docker image
docker build -t stock-api -f backend/Dockerfile .

# Jalankan container
docker run -p 8080:8080 -e PORT=8080 stock-api
```

---

## 3. Panduan Deploy ke Google Cloud Run

### Persiapan:
1. Pastikan Google Cloud SDK (`gcloud`) telah terpasang dan login:
   ```bash
   gcloud auth login
   gcloud config set project <PROJECT_ID_ANDA>
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
  --dockerfile backend/Dockerfile \
  --platform managed \
  --region asia-southeast2 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1
```

Setelah selesai, Google Cloud Run akan memberikan URL HTTPS publik layanan Anda (contoh: `https://stock-forecast-api-xxxxx-as.a.run.app`).
