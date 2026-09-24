# MLOps Stock Forecasting - Deep Learning Pipeline & Edge Inference

Proyek end-to-end MLOps untuk peramalan harga saham temporal perbankan Indonesia (BBCA.JK, BBRI.JK, dll.) menggunakan arsitektur Deep Learning (**LSTM** & **GRU**) dengan **Hyperparameter Grid Search** otomatis berbasis DVC, pemisahan modular pipeline (Ingestion, Modeling, Store), penyimpanan artefak langsung dari file biner **Parquet** & **JSON**, penyalinan aset terisolasi ke `web/backend/assets` (tanpa traversal relatif `../..`), serta inferensi performa tinggi melalui Cloudflare Workers (Nitro/Hono + TensorFlow.js + hyparquet) dan dashboard interaktif Cloudflare Pages (React 19 + TanStack + Astryx Design).

---

## 🏗️ Arsitektur Pipeline & Deployment

```text
[ Yahoo Finance API ]
        │
        ▼ (Stage 1: ingestion - python -m src.ingestion --ticker {ticker})
[ artifact/data/{ticker}.parquet ] ──(dvc push)──► [ Cloudflare R2 ]
        │
        ▼ (Stage 2: ml_pipeline - papermill src/ml_pipeline.ipynb)
┌────────────────────────────────────────────────────────┐
│  Hyperparameter Grid Search (LSTM & GRU)              │
│  ├─ Parameter: Time Steps, Optimizer, Batch, LR, Epoch │
│  ├─ Model Selection: Evaluasi RMSE, MAPE, & R²        │
│  ├─ Simpan Model: {ticker}_LSTM.keras, {ticker}_GRU    │
│  └─ Riwayat Eksperimen: {ticker}_hyperparameter.parquet│
└────────────────────────────────────────────────────────┘
        │
        ▼ (Stage 3: store - python -m src.store --ticker {ticker})
┌────────────────────────────────────────────────────────┐
│  Penyimpanan Artefak & Salin ke Backend (src/store.py) │
│  ├─ Normalisasi Skala: artifact/model/{ticker}_scaler.json
│  ├─ Metadata Metrik: artifact/model/{ticker}_metrics.json
│  └─ Copy Backend: web/backend/assets/{ticker}.*        │
└────────────────────────────────────────────────────────┘
        │
        ▼ (Deployment: Nitro Server Assets Bundle)
   ┌────┴───────────────────────────┐
   ▼                                ▼
[ Cloudflare Workers Backend ]    [ Cloudflare Pages Frontend ]
  ├─ Nitro + Hono API Runtime       ├─ React 19 + TanStack Router
  ├─ TensorFlow.js Edge Inference   ├─ Astryx Design System
  ├─ hyparquet Binary Engine        ├─ Wawasan Hyperparameter Optimal
  ├─ Direct web/backend/assets      └─ Visualisasi Chart Interaktif
  └─ Endpoint: /api/predict
```

---

## 📁 Struktur Direktori

```text
MLOps-Stock-Forecasting/
├── .github/
│   └── workflows/
│       └── pipeline.yml          # GitHub Actions CI/CD (Ingestion, Train, Store, Deploy)
├── artifact/
│   ├── data/                     # Dataset harga pasar historis biner (.parquet)
│   ├── model/                    # Model Keras (.keras), hyperparameter.parquet, scaler & metrics JSON
│   └── notebook/                 # Notebook hasil eksekusi Papermill & CML reports
├── src/
│   ├── config.py                 # Konfigurasi path pipeline
│   ├── ingestion.py              # Pengunduh data Yahoo Finance (murni Parquet)
│   ├── ml_pipeline.ipynb         # Notebook ML: Grid Search LSTM/GRU, evaluasi, & plotting
│   └── store.py                  # Penyimpanan scaler JSON, metrics JSON, & copy backend assets
├── web/
│   ├── backend/                  # API Serverless Nitro + Hono + TensorFlow.js Edge + hyparquet
│   │   ├── assets/               # Aset Parquet & JSON lokal mandiri (bebas dari traversal ../..)
│   │   ├── src/
│   │   │   ├── configs/          # Konfigurasi runtime backend
│   │   │   ├── data/             # Data access layer (pembacaan langsung Parquet via hyparquet)
│   │   │   ├── routes/           # Routing API (/api/stocks, /api/models, /api/predict)
│   │   │   ├── services/         # Engine peramalan adaptif TensorFlow.js
│   │   │   └── utils/            # Asset reading helper (Nitro serverAssets & fs fallback)
│   │   └── nitro.config.ts       # Konfigurasi Nitro serverAssets (dir: ./assets)
│   └── frontend/                 # Web Dashboard React 19 + Astryx Design System
│       ├── src/
│       │   ├── components/       # ForecastChart, ForecastModelInsights, ForecastTable
│       │   ├── routes/           # TanStack Router (Prediksi & Histori)
│       │   └── stores/           # Zustand state management
│       └── vite.config.ts
├── dvc.yaml                      # Definisi tahapan pipeline MLOps deklaratif (DAG)
├── params.yaml                   # Konfigurasi hyperparameter grid search & dataset
├── pyproject.toml                # Manajemen dependensi Python (Poetry)
└── README.md
```

---

## ⚙️ Konfigurasi Pipeline (`params.yaml`)

```yaml
TICKERS:
  - BBCA.JK
  - BBRI.JK
START_DATE: "2021-09-03"
END_DATE: "2026-09-03"

TARGET_COL: "close"
RANDOM_STATE: 42
TRAIN_SIZE: 0.8
EPOCHS: 50

# Hyperparameter
TIME_STEPS:
  - 10
  - 20
  - 30
OPTIMIZERS:
  - SGD
  - Adam
  - RMSprop
BATCH_SIZES:
  - 8
  - 16
  - 32
LEARNING_RATES:
  - 0.01
  - 0.001
  - 0.0001
MODELS:
  - LSTM
  - GRU
```

---

## 🛠️ Panduan Menjalankan Pipeline & Aplikasi

### 1. Menjalankan Pipeline MLOps (DVC)

```bash
# Jalankan seluruh tahapan pipeline (ingestion -> ml_pipeline -> store)
poetry run dvc repro

# Menampilkan grafik visual DAG pipeline
poetry run dvc dag
```

### 2. Tracking Eksperimen (DagsHub & MLflow)

Pelacakan eksperimen model, hyperparameter tuning, dan metrik otomatis direkam ke server DagsHub MLflow:
- **DagsHub MLflow Dashboard**: [https://dagshub.com/qoriib/MLOps-Stock-Forecasting.mlflow](https://dagshub.com/qoriib/MLOps-Stock-Forecasting.mlflow)

Untuk autentikasi di mesin baru:
```bash
poetry run dagshub login
```

### 3. Menjalankan Backend API Lokal

```bash
cd web/backend
npm install
npm run dev
```
API akan berjalan di `http://localhost:3000`.

### 3. Menjalankan Frontend Dashboard Lokal

```bash
cd web/frontend
npm install
npm run dev
```
Buka `http://localhost:3000` di browser untuk mengakses dashboard.

---

## 🌐 Otomasi CI/CD (GitHub Actions)

Alur kerja `.github/workflows/pipeline.yml` berjalan secara otomatis via jadwal mingguan atau pemicu manual:
1. **Ingestion**: Mengunduh data terbaru Yahoo Finance → `artifact/data/{ticker}.parquet`.
2. **ML Pipeline & Store**: Melatih model LSTM & GRU dengan hyperparameter tuning via Papermill, lalu mengeksekusi `src/store.py` untuk menghasilkan model `.keras`, `hyperparameter.parquet`, `scaler.json`, dan `metrics.json`, kemudian menyalin file yang dibutuhkan ke `web/backend/assets/`.
3. **Deploy Backend**: Membangun dan merilis API Nitro ke Cloudflare Workers dengan file Parquet & model dari `web/backend/assets/` tersemat langsung.
4. **Deploy Frontend**: Membangun aplikasi web dan mempublikasikannya ke Cloudflare Pages.
