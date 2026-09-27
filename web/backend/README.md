# Stock Forecast Inference Backend (FastAPI on Azure Container Apps)

A machine learning inference backend powered by **Python FastAPI** designed to serve stock price forecasting using **Keras LSTM/GRU** models, MinMaxScaler, MongoDB Time Series collection with **Beanie ODM**, and historical stock market data caching.

---

## 🚀 Key Features

- **FastAPI Native**: High performance with automated OpenAPI Swagger documentation (`/docs`) and root metadata check (`/`).
- **Clean Architecture & Separation of Concerns**: Clear separation across Routes, Controllers, Services, and Models/Entities.
- **MongoDB Time Series Collection & Beanie ODM**: High-performance time series data storage utilizing MongoDB native Time Series collections (`timeField="timestamp"`, `metaField="metadata"`, `granularity="hours"`) and Beanie async ODM.
- **Real ML Inference**: Loads trained `.keras` models directly using Keras/TensorFlow for multi-step autoregressive inference.
- **Structured Validation**: Pydantic v2 input validation with clear, informative error messages.

---

## 🛠️ Directory Structure

```text
web/backend/
├── app/
│   ├── config.py                  # Environment paths & MongoDB settings configuration
│   ├── main.py                    # FastAPI initialization, CORS, lifespan, & route registry
│   ├── controllers/               # Business logic controller layer
│   │   ├── models_controller.py   # Model overview & forecast execution
│   │   └── stocks_controller.py   # Historical stock price queries
│   ├── models/
│   │   ├── entities.py            # Beanie TimeSeries Document entity (StockPrice)
│   │   └── schemas.py             # Pydantic v2 request & response schemas
│   ├── routes/                    # API route declarations & parameter validation
│   │   ├── models.py              # GET /api/models & POST /api/models/predict
│   │   └── stocks.py              # GET /api/stocks/{ticker}
│   └── services/                  # Core service layer
│       ├── database_service.py    # PyMongo client & Beanie ODM lifespan initialization
│       ├── stock_service.py       # Stock data queries & time series history operations
│       └── model_service.py       # ML model inference & autoregressive forecast
├── assets/                        # Model & scaler assets
├── gunicorn.conf.py               # Production ASGI server configuration
├── main.py                        # Entrypoint ASGI application runner
└── requirements.txt               # Python package dependencies
```

---

## 💻 Running Locally

1. Navigate to the backend directory:
   ```bash
   cd web/backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the FastAPI development server:
   ```bash
   uvicorn main:app --port 8000 --reload
   ```
