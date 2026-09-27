from unittest.mock import AsyncMock, patch
from app.models.schemas import HistoricalItem, HistoricalResponse


# ============================================================================
# GET /api/stocks/{ticker} Tests with BVA (Boundary Value Analysis)
# ============================================================================

def test_stocks_ticker_below_min_length(client):
    """BVA: Ticker length below minimum boundary (len=1 < min_length=2)."""
    response = client.get("/api/stocks/A?start_date=2026-01-01&end_date=2026-01-10")
    assert response.status_code == 422


def test_stocks_ticker_at_min_length(client):
    """BVA: Ticker length at minimum boundary (len=2 == min_length=2).
    Passes schema validation, returns 404 as ticker is not in available assets.
    """
    response = client.get("/api/stocks/BB?start_date=2026-01-01&end_date=2026-01-10")
    assert response.status_code == 404
    assert "Ticker 'BB' not found" in response.json()["detail"]


def test_stocks_ticker_at_max_length(client):
    """BVA: Ticker length at maximum boundary (len=20 == max_length=20).
    Passes schema validation, returns 404 as 20-char ticker is not enrolled.
    """
    twenty_char_ticker = "A" * 20
    response = client.get(f"/api/stocks/{twenty_char_ticker}?start_date=2026-01-01&end_date=2026-01-10")
    assert response.status_code == 404
    assert f"Ticker '{twenty_char_ticker}' not found" in response.json()["detail"]


def test_stocks_ticker_above_max_length(client):
    """BVA: Ticker length above maximum boundary (len=21 > max_length=20)."""
    response = client.get(f"/api/stocks/{'A' * 21}?start_date=2026-01-01&end_date=2026-01-10")
    assert response.status_code == 422


def test_stocks_ticker_invalid_characters(client):
    """BVA: Ticker containing characters outside allowed regex pattern."""
    response = client.get("/api/stocks/BBCA$JK?start_date=2026-01-01&end_date=2026-01-10")
    assert response.status_code == 422


def test_stocks_date_format_invalid(client):
    """BVA: Date query string with invalid format."""
    response = client.get("/api/stocks/BBCA.JK?start_date=2026/01/01&end_date=2026-01-10")
    assert response.status_code == 422


def test_stocks_date_range_start_after_end(client):
    """BVA: Date range where start_date > end_date returns 400 Bad Request."""
    response = client.get("/api/stocks/BBCA.JK?start_date=2026-01-10&end_date=2026-01-01")
    assert response.status_code == 400
    assert "cannot be after end_date" in response.json()["detail"]


def test_stocks_date_range_equal_dates(client):
    """BVA: Date range at lower boundary where start_date == end_date (single day)."""
    mock_history = HistoricalResponse(
        ticker="BBCA.JK",
        data=[
            HistoricalItem(
                date="2026-01-05",
                open=10000.0,
                high=10200.0,
                low=9950.0,
                close=10150.0,
                volume=50000000.0,
            )
        ],
    )

    with patch("app.services.stock_service.StockService.get_stock_history", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_history
        response = client.get("/api/stocks/BBCA.JK?start_date=2026-01-05&end_date=2026-01-05")
        assert response.status_code == 200
        assert response.json()["ticker"] == "BBCA.JK"
        assert len(response.json()["data"]) == 1


def test_stocks_history_not_found(client):
    """Test 404 returned when no historical data exists for requested period."""
    with patch("app.services.stock_service.StockService.get_stock_history", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None
        response = client.get("/api/stocks/BBCA.JK?start_date=2026-01-01&end_date=2026-01-10")
        assert response.status_code == 404
        assert "No historical price data found" in response.json()["detail"]
