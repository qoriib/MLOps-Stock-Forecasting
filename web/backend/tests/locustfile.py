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
    Skenario Extreme Stress Testing Bertahap Hingga 200 CCU:
    - Stage 1:  10 CCU (Baseline & Warm-up)       -> Durasi: 0 - 60 detik (1 mnt)
    - Stage 2:  50 CCU (Beban Reguler)            -> Durasi: 60 - 150 detik (1.5 mnt)
    - Stage 3: 100 CCU (Beban Tinggi / High Load) -> Durasi: 150 - 270 detik (2 mnt)
    - Stage 4: 200 CCU (Peak Stress / Batas Maks) -> Durasi: 270 - 390 detik (2 mnt)
    - Stage 5:  20 CCU (Cool-down / Pemulihan)    -> Durasi: 390 - 450 detik (1 mnt)
    """
    stages = [
        {"duration": 60,  "users": 10,  "spawn_rate": 5},
        {"duration": 150, "users": 50,  "spawn_rate": 10},
        {"duration": 270, "users": 100, "spawn_rate": 15},
        {"duration": 390, "users": 200, "spawn_rate": 20},
        {"duration": 450, "users": 30,  "spawn_rate": 25},
    ]

    def tick(self):
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage["duration"]:
                return (stage["users"], stage["spawn_rate"])

        return None