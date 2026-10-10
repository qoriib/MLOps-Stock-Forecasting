import os
import datetime
from locust import HttpUser, task, between, LoadTestShape


class StockForecastUser(HttpUser):
    # Host target bawaan untuk inisialisasi test engine Azure Load Testing
    host = os.getenv("LOCUST_HOST") or "https://ca-stock-backend.eastasia.azurecontainerapps.io"

    # Jeda acak antar request per user simulasi (0.5 hingga 2 detik)
    wait_time = between(0.5, 2.0)

    def on_start(self):
        # Pastikan host aktif terpasang saat user instance dimulai
        if not self.host:
            self.host = os.getenv("LOCUST_HOST") or "https://ca-stock-backend.eastasia.azurecontainerapps.io"

    @task(1)
    def check_root(self):
        # Health check & root endpoint info
        self.client.get("/", name="GET / (Root Info)")

    @task(3)
    def get_models_overview(self):
        # Mengambil daftar model dan ticker yang tersedia
        self.client.get("/api/models", name="GET /api/models")

    @task(4)
    def get_stock_history(self):
        # Mengambil data harga historis saham BBCA.JK (rentang 30 hari terakhir)
        today = datetime.date.today()
        start_date = (today - datetime.timedelta(days=30)).isoformat()
        end_date = today.isoformat()
        self.client.get(
            f"/api/stocks/BBCA.JK?start_date={start_date}&end_date={end_date}",
            name="GET /api/stocks/BBCA.JK",
        )

    @task(2)
    def predict_stock_price(self):
        # Simulasi inferensi prediksi harga saham (beban komputasi tinggi)
        today = datetime.date.today()
        start_date = (today - datetime.timedelta(days=7)).isoformat()
        end_date = today.isoformat()

        payload = {
            "ticker": "BBCA.JK",
            "model": "lstm",
            "start_date": start_date,
            "end_date": end_date,
        }

        self.client.post(
            "/api/models/predict",
            json=payload,
            name="POST /api/models/predict (LSTM 7-Days)",
        )


class StepLoadShapeCCU(LoadTestShape):
    """
    Skenario Stress Testing Bertahap Hingga 1000 CCU:
    - Stage 1:   50 CCU (Baseline & Warm-up)               -> Durasi: 0 - 60 detik (1 mnt)
    - Stage 2:  100 CCU (Beban Rendah / Low Load)          -> Durasi: 60 - 120 detik (1 mnt)
    - Stage 3:  200 CCU (Beban Moderat / Moderate Load)    -> Durasi: 120 - 180 detik (1 mnt)
    - Stage 4:  350 CCU (Beban Operasional Tinggi)         -> Durasi: 180 - 240 detik (1 mnt)
    - Stage 5:  500 CCU (Beban Kapasitas Maksimal)         -> Durasi: 240 - 300 detik (1 mnt)
    - Stage 6:  700 CCU (Heavy Saturation / Scale-out)     -> Durasi: 300 - 360 detik (1 mnt)
    - Stage 7:  850 CCU (Pre-Peak Extreme Concurrency)     -> Durasi: 360 - 420 detik (1 mnt)
    - Stage 8: 1000 CCU (Peak Stress / Batas Maksimal)     -> Durasi: 420 - 510 detik (1.5 mnt)
    - Stage 9:   50 CCU (Cool-down & Recovery)             -> Durasi: 510 - 570 detik (1 mnt)
    """
    stages = [
        {"duration": 60,  "users": 50,   "spawn_rate": 10},
        {"duration": 120, "users": 100,  "spawn_rate": 15},
        {"duration": 180, "users": 200,  "spawn_rate": 20},
        {"duration": 240, "users": 350,  "spawn_rate": 25},
        {"duration": 300, "users": 500,  "spawn_rate": 30},
        {"duration": 360, "users": 700,  "spawn_rate": 35},
        {"duration": 420, "users": 850,  "spawn_rate": 40},
        {"duration": 510, "users": 1000, "spawn_rate": 45},
        {"duration": 570, "users": 50,   "spawn_rate": 50},
    ]

    def tick(self):
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage["duration"]:
                return (stage["users"], stage["spawn_rate"])

        return None