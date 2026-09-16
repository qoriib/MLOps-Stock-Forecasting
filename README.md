# MLOps Stock Forecasting - In-Browser Edge AI

Proyek end-to-end MLOps untuk peramalan harga saham (Stock Forecasting) menggunakan arsitektur Deep Learning recurrent neural networks (**LSTM** & **GRU**). Seluruh proses inferensi peramalan dijalankan secara **100% Client-Side di browser pengguna menggunakan TensorFlow.js (@tensorflow/tfjs)** dengan akselerasi perangkat keras WebGL/GPU.

---

## 🚀 Keunggulan Arsitektur In-Browser Edge AI

1. **Zero Server Cost & Infinite Scalability**: Tidak memerlukan server GPU/CPU inference backend (seperti Google Cloud Run atau VM) yang mahal. Web dapat di-host secara statis dan melayani jutaan pengguna secara gratis.
2. **Zero Latency**: Hasil inferensi peramalan multi-step dihitung seketika langsung di browser klien tanpa round-trip delay jaringan.
3. **Privasi & Keamanan Penuh**: Parameter inferensi dan manipulasi rentang data berjalan lokal di sisi klien.
4. **Offline-Capable**: Aplikasi tetap dapat melakukan inferensi peramalan tanpa koneksi internet setelah aset statis ter-cache di browser.

---

## 🏗️ Arsitektur Pipeline & Deployment

```text
[ Yahoo Finance API ]
        │
        ▼ (ingestion)
[ artifact/data/{ticker}.csv ] ──(dvc push)──► [ Cloudflare R2 ] (S3 Storage)
        │
        ▼ (ml_pipeline)
[ artifact/model/{ticker}_LSTM.keras ] ──(dvc push)──► [ Cloudflare R2 ]
[ artifact/model/{ticker}_GRU.keras  ]
        │
        ▼ (export_web: src/export_web_models.py)
[ web/frontend/public/data/{ticker}.json ]
[ web/frontend/public/models/overview.json ]
        │
        ▼ (build & deploy)
[ Cloudflare Pages / Static Hosting ]
        │
        ▼ (Client Browser)
┌────────────────────────────────────────────────────────┐
│  Browser Client Runtime (TanStack + React + ApexChart) │
│  └─► TensorFlow.js Engine (WebGL Accelerated)         │
│      ├─ In-Browser LSTM / GRU Model Evaluation         │
│      ├─ Autoregressive Multi-step Forecasting          │
│      └─ 95% Confidence Interval Calculation            │
└────────────────────────────────────────────────────────┘
```

---

## 📁 Struktur Direktori

```text
MLOps-Stock-Forecasting/
├── .github/
│   └── workflows/
│       └── pipeline.yml          # GitHub Actions CI/CD (Ingestion, Train, Export, Deploy)
├── artifact/
│   ├── data/                     # Dataset harga saham mentah (.csv) - dilacak DVC
│   └── model/                    # Model terlatih Keras (.keras), scaler & metrik - dilacak DVC
├── src/
│   ├── config.py                 # Konfigurasi path dan environment pipeline
│   ├── export_web_models.py      # Ekspor data & metadata model ke web static assets
│   ├── ingestion.py              # Pengunduh data historis Yahoo Finance
│   └── ml_pipeline.ipynb         # Notebook pelatihan & evaluasi LSTM & GRU
├── web/
│   └── frontend/                 # Aplikasi Web Modern (React 19 + TanStack + Astryx Design)
│       ├── public/
│       │   ├── data/             # JSON harga historis per ticker (BBCA, BBRI, dll)
│       │   └── models/           # overview.json metadata model & metrik
│       ├── src/
│       │   ├── configs/          # Konfigurasi aplikasi & URL aset
│       │   ├── services/
│       │   │   └── tfjsForecast.service.ts # Engine inferensi TensorFlow.js in-browser
│       │   ├── stores/           # Manajemen state global Zustand
│       │   └── routes/           # Routing TanStack Router (Forecast & History)
│       └── package.json
├── dvc.yaml                      # Definisi pipeline MLOps deklaratif
├── params.yaml                   # Parameter konfigurasi pelatihan & dataset
├── pyproject.toml                # Konfigurasi Poetry & dependensi Python
└── README.md
```

---

## 🛠️ Panduan Memulai Cepat (Local Development)

### 1. Menjalankan Dashboard Web Lokal

Aplikasi web dapat langsung dijalankan tanpa perlu menyalakan backend Python apa pun:

```bash
cd web/frontend
npm install
npm run dev
```

Buka browser di `http://localhost:3000`. Dashboard akan langsung memuat data pasar dan menjalankan inferensi LSTM/GRU via WebGL.

### 2. Memperbarui Data Pasar & Ekspor Web Aset

Jalankan script ekspor untuk memperbarui data JSON di `web/frontend/public/`:

```bash
# Menggunakan Python bawaan (Zero-Dependency)
python3 src/export_web_models.py

# Atau menggunakan environment Poetry
poetry run python -m src.export_web_models
```

### 3. Menjalankan Pipeline MLOps (DVC)

Untuk melatih ulang model dan mengekspor seluruh artefak:

```bash
# Menjalankan seluruh tahapan pipeline
poetry run dvc repro

# Sinkronisasi ke Cloudflare R2 Remote Storage
poetry run dvc push
```

---

## 🌐 Panduan Deployment ke Cloudflare Pages

Frontend web dikompilasi menjadi artefak statis murni yang siap disajikan melalui CDN global Cloudflare Pages:

```bash
cd web/frontend

# 1. Build bundle produksi
npm run build

# 2. Deploy ke Cloudflare Pages
npx wrangler pages deploy .output/public --project-name stock-forecasting-web
```

---

## ⚙️ Otomasi CI/CD (GitHub Actions)

Alur kerja `.github/workflows/pipeline.yml` berjalan secara terjadwal setiap hari Senin atau dapat dipicu secara manual via `workflow_dispatch`:
1. **Ingestion**: Mengunduh pembaruan harga saham terbaru dari Yahoo Finance.
2. **DVC Pipeline**: Melatih model LSTM & GRU, menghitung metrik evaluasi (RMSE, MAPE, R2), dan mengekspor notebook CML.
3. **Export Web**: Mengonversi dataset dan model metadata menjadi aset static web di `web/frontend/public/`.
4. **Deploy Frontend**: Melakukan build frontend dan mempublikasikannya langsung ke Cloudflare Pages.
