# MLOps Stock Forecasting

Proyek MLOps untuk peramalan harga saham (Stock Forecasting) menggunakan time-series dan machine learning, terintegrasi dengan DVC dan Poetry.

## Struktur Direktori
- `src/`: Modul kode sumber Python (ingestion, config, pipeline).
- `artifact/data/`: Direktori dataset yang dilacak dan dikelola oleh DVC.
- `dvc.yaml`: Definisi pipeline data DVC.
- `dvc.lock`: Catatan hash versi data dan dependensi pipeline DVC.
- `params.yaml`: Parameter konfigurasi pipeline.
- `pyproject.toml`: Konfigurasi dependensi project.

---

## Setup DVC Remote (Cloudflare R2)

Proyek ini menggunakan **Cloudflare R2** sebagai remote storage data DVC (kompatibel dengan protokol S3 API tanpa biaya egress).

### 1. Prasyarat Kredensial R2
Dapatkan informasi berikut dari dashboard Cloudflare:
- **Account ID**: Lihat di panel kanan menu **R2 Overview** atau URL dashboard.
- **Bucket Name**: Nama bucket R2 yang telah dibuat (contoh: `dvc-stock`).
- **R2 API Token**: Buka **R2** > **Manage R2 API Tokens** > **Create API Token** (izin *Object Read & Write*), dapatkan **Access Key ID** dan **Secret Access Key**.

### 2. Konfigurasi Remote & Endpoint URL
Daftarkan remote Cloudflare R2 dan atur endpoint URL:

```powershell
# 1. Daftarkan bucket sebagai default remote
dvc remote add -d r2 s3://dvc-stock

# 2. Atur S3 endpoint ke Cloudflare R2 (ganti <ACCOUNT_ID> dengan milik Anda)
dvc remote modify r2 endpointurl https://<ACCOUNT_ID>.r2.cloudflarestorage.com

# 3. Atur region ke auto
dvc remote modify r2 region auto
```

### 3. Konfigurasi Kredensial Lokal
> [!IMPORTANT]
> **Selalu gunakan flag `--local`** agar kredensial tersimpan di `.dvc/config.local` yang sudah diabaikan oleh Git, sehingga tidak akan bocor ke repositori publik.

```powershell
dvc remote modify --local r2 access_key_id <ACCESS_KEY_ID>
dvc remote modify --local r2 secret_access_key <SECRET_ACCESS_KEY>
```

---

## Alur Kerja DVC & Pipeline

### Menjalankan Pipeline Data
Jalankan pipeline DVC berdasarkan konfigurasi di `dvc.yaml` dan `params.yaml`:
```powershell
# Menjalankan seluruh tahapan pipeline (reproduce)
dvc repro
```

Atau menjalankan ingestion secara manual:
```powershell
python -m src.ingestion --symbols BBCA --start 2021-09-03 --end 2026-09-03
```

### Sinkronisasi Data ke Cloudflare R2
```powershell
# Upload data/artifact lokal ke remote Cloudflare R2
dvc push

# Download data/artifact dari remote Cloudflare R2 ke lokal
dvc pull

# Cek status perubahan pipeline dan data
dvc status
```

---

## Best Practice Commit Git & DVC
- **Commit ke Git**: Kode sumber (`src/`), konfigurasi umum (`.dvc/config`, `dvc.yaml`, `dvc.lock`, `params.yaml`, `pyproject.toml`).
- **Jangan commit ke Git**: File `.env`, `.dvc/config.local`, cache `.dvc/cache/`, dan file data fisik di `artifact/data/`.

