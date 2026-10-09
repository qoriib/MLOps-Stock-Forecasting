# Stock Forecast Inference Backend

Backend inferensi machine learning berbasis FastAPI untuk melayani peramalan harga saham menggunakan model Keras LSTM/GRU, normalisasi MinMaxScaler, penyimpanan MongoDB Time Series dengan Beanie ODM, dan pengujian beban performa Locust.

---

## Fitur Utama

- **FastAPI Native**: Dokumentasi interaktif otomatis OpenAPI Swagger (`/docs`) dan health check (`/`).
- **Clean Architecture**: Pemisahan tanggung jawab yang jelas antara Routes, Controllers, Services, dan Models/Entities.
- **MongoDB Native Time Series**: Menggunakan koleksi deret waktu native (`timestamp`, `metadata.ticker`, granularity `hours`) via Beanie ODM.
- **Autoregressive Forecast**: Inferensi sekuensial multi-langkah berbasis jendela waktu (`time_steps`) dengan memperhitungkan hari bursa aktif.
- **Load Testing (CCU 10-150)**: Pengujian beban bertahap menggunakan Locust untuk menguji kestabilan throughput dan latensi.

---

## Struktur Direktori

```text
web/backend/
├── app/
│   ├── config.py              # Konfigurasi path dan environment MongoDB
│   ├── main.py                # Inisialisasi FastAPI, CORS, lifespan, dan routing
│   ├── controllers/           # Handler controller endpoint
│   ├── models/                # Pydantic schemas dan entity Beanie TimeSeries
│   ├── routes/                # Deklarasi route (/api/models, /api/stocks)
│   └── services/              # Logika database, caching saham, dan inferensi ML
├── assets/                    # Model .keras dan scaler .pkl aktif
├── tests/                     # Suite pengujian beban Locust
│   ├── locustfile.py          # Definisi user tasks dan StepLoadShape (CCU 10-150)
│   └── run_load_test.py       # Script runner headless dan generator report Markdown
├── gunicorn.conf.py           # Konfigurasi server produksi ASGI
├── main.py                    # Entrypoint aplikasi ASGI
└── requirements.txt           # Dependensi paket Python
```

---

## Menjalankan Secara Lokal

1. Masuk ke direktori backend:
   ```bash
   cd web/backend
   ```
2. Buat dan aktifkan virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Pasang dependensi:
   ```bash
   pip install -r requirements.txt
   ```
4. Jalankan server FastAPI:
   ```bash
   uvicorn main:app --port 8000 --reload
   ```
   Akses dokumentasi Swagger di `http://localhost:8000/docs`.

---

## Load Testing (CCU 10-150)

Pengujian beban backend dilakukan menggunakan Locust dengan skenario bertahap 10 hingga 150 Concurrent Users (CCU):

### 1. Mode Otomatis (Headless)
```bash
python tests/run_load_test.py --host http://localhost:8000 --users 150 --spawn-rate 20 --run-time 1m
```
Hasil pengujian disimpan di direktori `tests/result/` dalam format file CSV.

### 2. Mode Web Dashboard Interaktif
```bash
locust -f tests/locustfile.py --host http://localhost:8000
```
Buka peramban di `http://localhost:8089` untuk memantau grafik CCU dan response time secara real-time.
