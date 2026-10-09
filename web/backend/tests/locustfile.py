import datetime
from locust import HttpUser, task, between, LoadTestShape


class StockForecastUser(HttpUser):
    # Jeda acak antar request per user simulasi (0.5 hingga 2 detik)
    wait_time = between(0.5, 2.0)

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
    Skenario beban bertahap (Ramping Step Load) dari CCU 10 hingga 150:
    - Stage 1: 10 CCU  (Baseline / Warmup) -> 30 detik
    - Stage 2: 30 CCU  (Normal Load)       -> 30 detik
    - Stage 3: 75 CCU  (Moderate Load)     -> 30 detik
    - Stage 4: 120 CCU (High Load)         -> 30 detik
    - Stage 5: 150 CCU (Peak Stress Load)  -> 30 detik
    """
    stages = [
        {"duration": 30,  "users": 10,  "spawn_rate": 5},
        {"duration": 60,  "users": 30,  "spawn_rate": 10},
        {"duration": 90,  "users": 75,  "spawn_rate": 15},
        {"duration": 120, "users": 120, "spawn_rate": 20},
        {"duration": 150, "users": 150, "spawn_rate": 25},
    ]

    def tick(self):
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage["duration"]:
                return (stage["users"], stage["spawn_rate"])

        # Selesai setelah semua tahapan terlewati
        return None
