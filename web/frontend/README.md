# Stock Forecasting Web Frontend (React 19 + TanStack + Astryx Design)

Aplikasi web dashboard interaktif untuk visualisasi peramalan harga saham temporal perbankan menggunakan **React 19**, **TanStack Router**, **Astryx Design System**, dan charting interaktif **ApexCharts**.

---

## ⚡ Fitur Utama

- **Interactive Forecast Visualization:** Chart multi-step peramalan harga saham dengan interval keyakinan 95%.
- **Optimal Model Insights:** Menampilkan parameter hyperparameter terbaik (sequence window, optimizer, batch size, learning rate) dan metrik evaluasi data uji (RMSE, MAPE, R²).
- **Astryx Design System:** Antarmuka responsif dan aksesibel dengan dukungan tema gelap (*dark mode*) dan terang (*light mode*).
- **State Management:** Terkoordinasi via **Zustand** store.
- **Serverless Edge Ready:** Di-build menggunakan **Nitro** untuk deployment ke Cloudflare Pages.

---

## 🛠️ Panduan Menjalankan Lokal

```bash
cd web/frontend
npm install
npm run dev
```

Buka `http://localhost:3000` di browser Anda.

---

## 🏗️ Kompilasi Produksi

```bash
npm run build
```

Hasil build statis dan worker adapter akan disimpan di direktori `dist/` dan `.output/`.
