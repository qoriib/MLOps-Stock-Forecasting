# Stock Forecast API (Hono + Cloudflare Workers)

Backend serverless berbasis **TypeScript** dan framework **[Hono](https://hono.dev)** yang di-deploy di **Cloudflare Workers** dengan kapabilitas inferensi edge menggunakan **[TensorFlow.js](https://js.tensorflow.org)** CPU backend.

---

## ⚡ Fitur Utama

- **Ultra Low Latency:** Dijalankan di ratusan titik Cloudflare edge global.
- **Zero Server Maintenance:** Arsitektur *serverless* tanpa perlu mengelola VM / Docker container.
- **Edge Inference:** Inferensi model peramalan deret waktu autoregressive (LSTM & GRU) langsung di worker via TensorFlow.js.
- **Ringan & Kompatibel:** Ukuran bundle terkompresi ~143 KiB dengan flag `nodejs_compat`.

---

## 🛠️ API Endpoints

| Method | Endpoint | Deskripsi |
|---|---|---|
| `GET` | `/` | Status API & daftar rute |
| `GET` | `/health` | Pemeriksaan kesehatan service |
| `GET` | `/api/models` | Ringkasan model, ticker yang didukung, dan metrik evaluasi |
| `GET` | `/api/stocks/:ticker` | Data riwayat harga saham (parameter: `limit`, `start_date`, `end_date`) |
| `POST` | `/api/predict` | Menjalankan inferensi peramalan harga saham multi-step |

### Contoh Request Prediksi (`POST /api/predict`):
```json
{
  "ticker": "BBCA.JK",
  "model_type": "lstm",
  "steps": 30
}
```

---

## 🚀 Menjalankan Secara Lokal

```bash
cd web/backend
npm install
npm run dev
```
Worker akan berjalan di `http://localhost:8787`.

---

## 🚢 Deployment ke Cloudflare Workers

```bash
npm run deploy
```
Atau otomatis melalui pipeline CI/CD GitHub Actions.
