# Stock Forecast Inference Backend (FastAPI on Azure Container Apps)

Backend inferensi machine learning berbasis **Python FastAPI** yang dirancang untuk melayani peramalan harga saham menggunakan model **Keras LSTM/GRU**, scaler MinMaxScaler, MongoDB Time Series collection dengan **Beanie ODM**, dan caching data historis pasar saham.

---

## 🚀 Fitur Utama

- **FastAPI Native**: Kinerja tinggi dengan dokumentasi OpenAPI Swagger otomatis (`/docs`) dan root metadata check (`/`).
- **Clean Architecture & Separation of Concerns**: Pemisahan jelas antara Routes, Controllers, Services, dan Models/Entities.
- **MongoDB Time Series Collection & Beanie ODM**: Penyimpanan data deret waktu harga saham berkinerja tinggi menggunakan MongoDB Time Series native collection (`timeField="timestamp"`, `metaField="metadata"`, `granularity="hours"`) dan Beanie async ODM.
- **Real ML Inference**: Memuat model `.keras` terlatih langsung menggunakan Keras/TensorFlow dengan fallback ke simulation engine.
- **Validasi Terstruktur**: Validasi input Pydantic v2 dengan pesan error yang informatif.

---

## 🛠️ Struktur Direktori

```text
web/backend/
├── app/
│   ├── config.py                  # Konfigurasi paths, environment, & MongoDB settings
│   ├── main.py                    # Inisialisasi FastAPI, CORS, lifespan, & route registry
│   ├── controllers/               # Business logic controller layer
│   │   ├── models_controller.py   # Overview model & eksekusi peramalan predict
│   │   └── stocks_controller.py   # Query riwayat harga saham
│   ├── models/
│   │   ├── entities.py            # Beanie TimeSeries Document entity (StockPrice)
│   │   └── schemas.py             # Pydantic v2 request & response schemas
│   ├── routes/                    # API route declarations & param validation
│   │   ├── models.py              # GET /api/models & POST /api/models/predict
│   │   └── stocks.py              # GET /api/stocks/{ticker}
│   └── services/                  # Core services layer
│       ├── database_service.py    # Motor client & Beanie ODM lifespan initialization
│       ├── stock_service.py       # Stock data queries & time series history operations
│       └── model_service.py       # ML model inference & autoregressive forecast
├── assets/                        # Model & data assets
├── gunicorn.conf.py               # Konfigurasi ASGI production
├── main.py                        # Entrypoint ASGI server
└── requirements.txt               # Dependensi Python
```

---

## 💻 Menjalankan di Lokal

1. Masuk ke direktori backend:
   ```bash
   cd web/backend
   ```
2. Buat dan aktifkan virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependensi:
   ```bash
   pip install -r requirements.txt
   ```
4. Jalankan server FastAPI:
   ```bash
   uvicorn main:app --port 8000 --reload
   ```
