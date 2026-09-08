# MLOps Stock Forecasting

Proyek end-to-end MLOps untuk peramalan harga saham (Stock Forecasting) menggunakan time-series dan machine learning (ARIMA & SARIMA), terintegrasi dengan DVC, ekosistem Cloudflare (R2, D1, Workers), dan antarmuka web modern.

---

## Arsitektur Ekosistem Cloudflare & Pipeline

```text
[ yfinance ]
     │
     ▼ (ingestion)
[ artifact/data/ ] ──(dvc push)──► [ Cloudflare R2 ] (S3-compatible Object Storage)
     │
     ▼ (ml_pipeline)
[ artifact/forecast/ ]
     │
     ▼ (src/store.py)
[ artifact/seed.sql ] ──────────► [ Cloudflare D1 ] (Edge SQLite Database)
                                         │
                                         ▼ (D1 Binding 'DB')
                              [ Cloudflare Workers (Hono) ] (REST API)
                                         │
                                         ▼ (Fetch JSON API)
                              [ Frontend (React/Vite) ]
```

---

## Struktur Direktori
- `src/`: Modul kode sumber Python:
  - `ingestion.py`: Mengunduh data saham dari yfinance.
  - `config.py`: Definisi path direktori dan file artefak.
  - `ml_pipeline.ipynb`: Pipeline pemodelan dan peramalan time-series (ARIMA & SARIMA).
  - `store.py`: Generator seed SQL untuk Cloudflare D1.
- `artifact/`:
  - `data/`: Dataset harga historis saham (diabaikan Git, dilacak DVC).
  - `forecast/`: Hasil prediksi peramalan masa depan (diabaikan Git, dilacak DVC).
  - `seed.sql`: File SQL seed otomatis untuk Cloudflare D1.
- `web/`:
  - `backend/`: Serverless REST API berbasis Cloudflare Workers & Hono dengan binding Cloudflare D1.
  - `frontend/`: Aplikasi dashboard interaktif React / Vite.
- `dvc.yaml`: Definisi pipeline data & model DVC (`ingestion -> ml_pipeline -> store`).
- `dvc.lock`: Hash versi data dan state stage DVC.
- `params.yaml`: Parameter konfigurasi pipeline (`tickers`, `start_date`, `end_date`, `train_size_ratio`, `target_col`, `forecast_steps`).

---

## Panduan Setup Layanan Cloudflare

### 1. Cloudflare R2 (DVC Remote Storage)

Cloudflare R2 digunakan sebagai remote storage untuk melacak dan menyimpan dataset besar serta artefak model tanpa biaya egress.

#### A. Dapatkan Kredensial R2 dari Dashboard
1. Buka dashboard Cloudflare: [dash.cloudflare.com](https://dash.cloudflare.com/).
2. Masuk ke menu **R2** > klik **Create bucket** (misal: `dvc-stock`).
3. Salin **Account ID** pada panel sebelah kanan halaman Overview R2.
4. Buat API Token untuk R2:
   - Masuk ke **Manage R2 API Tokens** > **Create API Token**.
   - Pilih izin **Object Read & Write**.
   - Simpan **Access Key ID** dan **Secret Access Key**.

#### B. Konfigurasi DVC di Terminal
Jalankan perintah berikut di root folder proyek:

```powershell
# 1. Daftarkan bucket sebagai remote default
dvc remote add -d r2 s3://dvc-stock

# 2. Atur S3 endpoint ke Cloudflare R2 (ganti <ACCOUNT_ID>)
dvc remote modify r2 endpointurl https://<ACCOUNT_ID>.r2.cloudflarestorage.com

# 3. Atur region ke auto
dvc remote modify r2 region auto

# 4. Masukkan kredensial lokal (--local agar TIDAK ter-commit ke Git)
dvc remote modify --local r2 access_key_id <ACCESS_KEY_ID>
dvc remote modify --local r2 secret_access_key <SECRET_ACCESS_KEY>
```

#### C. Sinkronisasi Data R2
```powershell
# Upload artefak lokal ke Cloudflare R2
dvc push

# Download artefak dari Cloudflare R2 ke lokal
dvc pull

# Cek status perbedaan data
dvc status
```

---

### 2. Cloudflare D1 (Serverless SQL Database)

Cloudflare D1 menyimpan data harga saham dan hasil peramalan yang siap disajikan ke pengguna melalui query SQL di edge network.

#### A. Login ke Wrangler CLI
```powershell
npx wrangler login
```

#### B. Membuat Database D1
```powershell
cd web/backend
npx wrangler d1 create stock-db
```
Salin nilai `database_id` dari terminal.

#### C. Masukkan `database_id` ke `wrangler.jsonc`
Buka `web/backend/wrangler.jsonc` dan pastikan binding D1 telah terpasang:
```jsonc
{
  "$schema": "node_modules/wrangler/config-schema.json",
  "name": "backend",
  "main": "src/index.ts",
  "compatibility_date": "2026-09-08",
  "d1_databases": [
    {
      "binding": "DB",
      "database_name": "stock-db",
      "database_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    }
  ]
}
```

#### D. Menjalankan Seeding Data SQL ke D1
File seed SQL (`artifact/seed.sql`) dihasilkan secara otomatis dari pipeline DVC (`dvc repro` atau `python -m src.store`).

- **Eksekusi ke Database D1 Lokal (untuk development offline):**
  ```powershell
  cd web/backend
  npm run db:seed:local
  ```

- **Eksekusi ke Database D1 Remote / Production:**
  ```powershell
  cd web/backend
  npm run db:seed
  ```

#### E. Verifikasi Data di D1
```powershell
# Cek database lokal
npx wrangler d1 execute stock-db --local --command="SELECT COUNT(*) AS total_prices FROM stock_prices;"

# Cek database remote Cloudflare
npx wrangler d1 execute stock-db --remote --command="SELECT COUNT(*) AS total_prices FROM stock_prices;"
```

---

### 3. Cloudflare Workers (Backend Hono REST API)

Backend diimplementasikan menggunakan framework **Hono** di atas runtime Cloudflare Workers dengan integrasi langsung ke D1.

#### A. Menjalankan Server Development Lokal
```powershell
cd web/backend
npm run dev
```
Server development aktif di: `http://localhost:8787`

#### B. Endpoint API yang Disediakan:
- `GET /api/stocks`: Daftar seluruh saham yang tersedia di database.
- `GET /api/stocks/:symbol`: Riwayat harga dengan pagination (`limit`) dan filter tanggal (`start_date`, `end_date`, `order`).
- `GET /api/stocks/:symbol/latest`: Baris data harga terbaru.
- `GET /api/stocks/:symbol/summary`: Metrik ringkasan harga (harga terakhir, perubahan, min, max, rata-rata volume).
- `GET /api/stocks/:symbol/forecast`: Hasil peramalan masa depan (ARIMA/SARIMA).

#### C. Deploy Worker ke Cloudflare Network
```powershell
cd web/backend
npm run deploy
```

---

### 4. Cloudflare Pages / Frontend (React & Vite)

Frontend dashboard berada di direktori `web/frontend/`.

#### A. Konfigurasi Environment API
Buat file `web/frontend/.env`:
```env
# Gunakan URL lokal saat development:
VITE_API_BASE_URL=http://localhost:8787

# Atau URL worker production saat deploy:
# VITE_API_BASE_URL=https://backend.<subdomain>.workers.dev
```

#### B. Menjalankan Frontend secara Lokal
```powershell
cd web/frontend
npm install
npm run dev
```
Buka browser di `http://localhost:5173`.

#### C. Deploy Frontend ke Cloudflare Pages
```powershell
cd web/frontend
npm run build
npx wrangler pages deploy dist --project-name stock-forecasting-web
```

---

## Alur Kerja DVC & Pipeline

Pipeline MLOps dikelola secara deklaratif menggunakan `dvc.yaml` dengan dukungan **Stage Matrix** untuk pemrosesan 5 ticker perbankan secara paralel.

### Visualisasi Pipeline (DAG)
Jalankan perintah berikut untuk melihat struktur Directed Acyclic Graph:
```powershell
dvc dag
```
```text
                                 +-----------+
                                 | ingestion |
                                 +-----------+
        /             /                |               \             \
+------------------+ +------------------+ +------------------+ +------------------+ +------------------+
| ml_pipeline@BBCA | | ml_pipeline@BBRI | | ml_pipeline@BMRI | | ml_pipeline@BBNI | | ml_pipeline@BBTN |
+------------------+ +------------------+ +------------------+ +------------------+ +------------------+
        \             \                |               /             /
                                   +-------+
                                   | store |
                                   +-------+
```

### Menjalankan Seluruh Pipeline
Jalankan seluruh tahapan pipeline berdasarkan konfigurasi di `dvc.yaml` dan `params.yaml`:
```powershell
# Menjalankan seluruh alur: ingestion -> ml_pipeline (5 ticker) -> store
dvc repro
```

### Menjalankan Per Tahap / Single Ticker:
1. **Hanya Ingestion Data Saham (yfinance)**:
   ```powershell
   dvc repro ingestion
   # atau: python -m src.ingestion
   ```

2. **Hanya Model Ticker Tertentu (contoh: BBRI)**:
   ```powershell
   dvc repro ml_pipeline@BBRI
   ```

3. **Hanya Generate Seed SQL Cloudflare D1**:
   ```powershell
   dvc repro store
   # atau: python -m src.store
   ```


---

## Cheatsheet Perintah

| Komponen | Perintah | Deskripsi |
|---|---|---|
| **DVC & R2** | `dvc repro` | Menjalankan seluruh pipeline MLOps |
| | `dvc push` | Mengunggah artefak ke Cloudflare R2 |
| | `dvc pull` | Mengunduh artefak dari Cloudflare R2 |
| **D1 Database** | `python -m src.store` | Membuat file `artifact/seed.sql` |
| | `cd web/backend; npm run db:seed:local` | Mengisi database D1 lokal |
| | `cd web/backend; npm run db:seed` | Mengisi database D1 Cloudflare remote |
| **Backend Hono** | `cd web/backend; npm run dev` | Menjalankan API backend lokal (`:8787`) |
| | `cd web/backend; npm run deploy` | Deploy Worker ke Cloudflare |
| **Frontend React** | `cd web/frontend; npm run dev` | Menjalankan dashboard frontend (`:5173`) |
| | `cd web/frontend; npm run build` | Build bundle frontend untuk production |
