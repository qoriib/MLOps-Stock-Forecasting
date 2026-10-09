# Stock Forecasting Web Frontend

Aplikasi dashboard web interaktif untuk visualisasi peramalan harga saham temporal perbankan menggunakan React 19, TanStack Router, Zustand, dan charting interaktif Apache ECharts.

---

## Fitur Utama

- **Visualisasi Peramalan Interaktif**: Menampilkan data historis pasar saham dan proyeksi peramalan multi-langkah ke masa depan.
- **Wawasan Model Terbaik**: Menyajikan metrik evaluasi (RMSE, MAPE, R²) dan hyperparameter model aktif.
- **Antarmuka Responsif**: Mendukung tema gelap (*dark mode*) dan terang (*light mode*).
- **Manajemen State**: Terpusat menggunakan Zustand store.

---

## Panduan Menjalankan Lokal

1. Masuk ke direktori frontend:
   ```bash
   cd web/frontend
   ```
2. Pasang dependensi:
   ```bash
   npm install
   ```
3. Jalankan development server:
   ```bash
   npm run dev
   ```
   Buka peramban di `http://localhost:3000`.

---

## Kompilasi Produksi

```bash
npm run build
```
Hasil build statis akan disimpan di direktori `dist/`.
