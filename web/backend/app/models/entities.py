from datetime import date, datetime
from typing import Any, Dict
from beanie import Document, Granularity, TimeSeriesConfig
from pydantic import BaseModel, Field

class StockMetadata(BaseModel):
    ticker: str = Field(description="Simbol ticker saham (misal: BBCA.JK)")

class StockPrice(Document):
    timestamp: datetime = Field(
        description="Waktu/tanggal pencatatan harga saham (UTC)"
    )
    metadata: StockMetadata = Field(
        description="Metadata pengelompokan time series (ticker saham)"
    )
    open: float = Field(default=0.0, description="Harga pembukaan")
    high: float = Field(default=0.0, description="Harga tertinggi")
    low: float = Field(default=0.0, description="Harga terendah")
    close: float = Field(default=0.0, description="Harga penutupan")
    volume: float = Field(default=0.0, description="Volume transaksi")

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
