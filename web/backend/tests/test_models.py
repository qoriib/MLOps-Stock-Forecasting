from unittest.mock import AsyncMock, patch
from app.models.schemas import PredictionItem, PredictResponse


# ============================================================================
# 1. GET /api/models Tests
# ============================================================================

def test_get_models_overview_success(client):
    """Test getting models overview returns valid status and structure."""
    response = client.get("/api/models")
    assert response.status_code == 200
    data = response.json()
    assert "tickers" in data
    assert "models" in data
    assert isinstance(data["tickers"], list)
    assert isinstance(data["models"], list)


# ============================================================================
# 2. POST /api/models/predict Tests with BVA (Boundary Value Analysis)
# ============================================================================

def test_predict_ticker_below_min_length(client):
    """BVA: Ticker length below minimum boundary (len=1 < min_length=2)."""
    payload = {
        "ticker": "A",
        "model": "lstm",
        "start_date": "2026-09-28",
        "end_date": "2026-10-02",
    }
    response = client.post("/api/models/predict", json=payload)
    assert response.status_code == 422


def test_predict_ticker_at_min_length(client):
    """BVA: Ticker length at minimum boundary (len=2 == min_length=2).
    Passes schema validation, returns 404 since 'BB' is not an enrolled model.
    """
    payload = {
        "ticker": "BB",
        "model": "lstm",
        "start_date": "2026-09-28",
        "end_date": "2026-10-02",
    }
    response = client.post("/api/models/predict", json=payload)
    assert response.status_code == 404
    assert "Ticker 'BB' not found" in response.json()["detail"]


def test_predict_ticker_at_max_length(client):
    """BVA: Ticker length at maximum boundary (len=20 == max_length=20).
    Passes schema validation, returns 404 since 20-char ticker is not enrolled.
    """
    twenty_char_ticker = "A" * 20
    payload = {
        "ticker": twenty_char_ticker,
        "model": "lstm",
        "start_date": "2026-09-28",
        "end_date": "2026-10-02",
    }
    response = client.post("/api/models/predict", json=payload)
    assert response.status_code == 404
    assert f"Ticker '{twenty_char_ticker}' not found" in response.json()["detail"]


def test_predict_ticker_above_max_length(client):
    """BVA: Ticker length above maximum boundary (len=21 > max_length=20)."""
    payload = {
        "ticker": "A" * 21,
        "model": "lstm",
        "start_date": "2026-09-28",
        "end_date": "2026-10-02",
    }
    response = client.post("/api/models/predict", json=payload)
    assert response.status_code == 422


def test_predict_ticker_invalid_characters(client):
    """BVA: Ticker containing characters outside allowed regex pattern ^[A-Za-z0-9.]+$."""
    payload = {
        "ticker": "BBCA$JK",
        "model": "lstm",
        "start_date": "2026-09-28",
        "end_date": "2026-10-02",
    }
    response = client.post("/api/models/predict", json=payload)
    assert response.status_code == 422


def test_predict_model_outside_boundary(client):
    """BVA: Model value outside valid set ['lstm', 'gru']."""
    payload = {
        "ticker": "BBCA.JK",
        "model": "transformer",
        "start_date": "2026-09-28",
        "end_date": "2026-10-02",
    }
    response = client.post("/api/models/predict", json=payload)
    assert response.status_code == 422


def test_predict_model_case_insensitive_boundary(client):
    """BVA: Model boundary with uppercase 'LSTM' and 'GRU' should be accepted and normalized."""
    mock_forecast = PredictResponse(
        ticker="BBCA.JK",
        model="lstm",
        predictions=[PredictionItem(date="2026-09-28", predicted_price=10500.0)],
    )

    with patch("app.services.model_service.ModelService.execute_forecast", new_callable=AsyncMock) as mock_exec:
        mock_exec.return_value = mock_forecast
        payload = {
            "ticker": "BBCA.JK",
            "model": "LSTM",
            "start_date": "2026-09-28",
            "end_date": "2026-09-28",
        }
        response = client.post("/api/models/predict", json=payload)
        assert response.status_code == 200
        assert response.json()["model"] == "lstm"


def test_predict_date_format_invalid(client):
    """BVA: Date string not matching pattern YYYY-MM-DD."""
    payload = {
        "ticker": "BBCA.JK",
        "model": "lstm",
        "start_date": "28-09-2026",
        "end_date": "2026-10-02",
    }
    response = client.post("/api/models/predict", json=payload)
    assert response.status_code == 422


def test_predict_date_range_equal_dates(client):
    """BVA: Date range at lower boundary where start_date == end_date (single day)."""
    mock_forecast = PredictResponse(
        ticker="BBCA.JK",
        model="lstm",
        predictions=[PredictionItem(date="2026-09-28", predicted_price=10000.0)],
    )

    with patch("app.services.model_service.ModelService.execute_forecast", new_callable=AsyncMock) as mock_exec:
        mock_exec.return_value = mock_forecast
        payload = {
            "ticker": "BBCA.JK",
            "model": "lstm",
            "start_date": "2026-09-28",
            "end_date": "2026-09-28",
        }
        response = client.post("/api/models/predict", json=payload)
        assert response.status_code == 200
        assert len(response.json()["predictions"]) == 1


def test_predict_date_range_start_after_end(client):
    """BVA: Date range above boundary where start_date > end_date (reversed dates)."""
    payload = {
        "ticker": "BBCA.JK",
        "model": "lstm",
        "start_date": "2026-10-02",
        "end_date": "2026-09-28",
    }
    response = client.post("/api/models/predict", json=payload)
    assert response.status_code == 422
    assert "start_date cannot be greater than end_date" in response.text
