# Stock Forecast Inference Backend (FastAPI on Azure App Service)

Backend inferensi machine learning berbasis **Python FastAPI** yang dirancang untuk melayani peramalan harga saham menggunakan model **Keras LSTM/GRU**, scaler MinMaxScaler, dan data historis berformat Parquet.

---

## 🚀 Fitur Utama

- **FastAPI Native**: Kinerja tinggi dengan dokumentasi OpenAPI Swagger otomatis (`/docs`).
- **Real ML Inference**: Memuat model `.keras` terlatih langsung menggunakan Keras/TensorFlow.
- **DVC Assets Integration**: Membaca dataset Parquet, scaler JSON, dan metrik langsung dari folder `web/backend/assets/`.
- **Azure App Service Ready**: Siap dideploy menggunakan Gunicorn + Uvicorn worker atau direct container.

---

## 🛠️ Struktur Direktori

```text
web/backend/
├── app/
│   ├── config.py              # Konfigurasi paths & parameter inferensi
│   ├── main.py                # Inisialisasi FastAPI & middleware CORS
│   ├── models/
│   │   └── schemas.py         # Pydantic schemas (typed API contract)
│   ├── routes/
│   │   ├── models.py          # GET /api/models
│   │   ├── stocks.py          # GET /api/stocks/{ticker}
│   │   └── predict.py         # POST /api/predict
│   └── services/
│       ├── data_service.py    # Handler data parquet, scaler, metrik
│       └── forecast_service.py # Engine inferensi autoregressive multi-step
├── assets/                    # Artefak model & data dari stage DVC 'store'
├── gunicorn.conf.py           # Konfigurasi WSGI/ASGI untuk Azure App Service
├── main.py                    # Root entrypoint ASGI
└── requirements.txt           # Dependensi Python
```

---

## 💻 Menjalankan di Lokal

1. Masuk ke direktori backend:
   ```bash
   cd web/backend
   ```
2. Install dependensi:
   ```bash
   pip install -r requirements.txt
   ```
3. Jalankan server FastAPI:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```
4. Buka dokumentasi interaktif di browser: [http://localhost:8000/docs](http://localhost:8000/docs)
