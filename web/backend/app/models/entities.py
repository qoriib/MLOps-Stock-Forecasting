from datetime import date, datetime
from typing import Any, Dict
from beanie import Document, Granularity, TimeSeriesConfig
from pydantic import BaseModel, Field

class StockMetadata(BaseModel):
    ticker: str = Field(description="Stock ticker symbol (e.g. BBCA.JK)")

class StockPrice(Document):
    timestamp: datetime = Field(
        description="Stock price recording timestamp (UTC)"
    )
    metadata: StockMetadata = Field(
        description="Time series grouping metadata (stock ticker)"
    )
    open: float = Field(default=0.0, description="Opening price")
    high: float = Field(default=0.0, description="Highest price")
    low: float = Field(default=0.0, description="Lowest price")
    close: float = Field(default=0.0, description="Closing price")
    volume: float = Field(default=0.0, description="Trading volume")

    class Settings:
        name = "stock_prices"
        timeseries = TimeSeriesConfig(
            time_field="timestamp",
            meta_field="metadata",
            granularity=Granularity.hours,
        )
        indexes = [
            [
                ("metadata.ticker", 1),
                ("timestamp", 1),
            ],
        ]

    @property
    def ticker(self) -> str:
        return self.metadata.ticker

    @property
    def date(self) -> date:
        return self.timestamp.date()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ticker": self.metadata.ticker,
            "date": self.timestamp.strftime("%Y-%m-%d"),
            "open": float(self.open),
            "high": float(self.high),
            "low": float(self.low),
            "close": float(self.close),
            "volume": float(self.volume),
        }

    def __repr__(self) -> str:
        return f"<StockPrice(ticker='{self.metadata.ticker}', date='{self.date}', close={self.close})>"
