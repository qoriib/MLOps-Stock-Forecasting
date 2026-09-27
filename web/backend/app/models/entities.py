import datetime
from typing import Any, Dict
from pydantic import BaseModel, Field
from beanie import Document, Granularity, TimeSeriesConfig

class StockMetadata(BaseModel):
    ticker: str

class StockPrice(Document):
    timestamp: datetime.datetime = Field(
        description="Waktu/tanggal pencatatan harga saham"
    )
    metadata: StockMetadata = Field(
        description="Metadata pengelompokan time series (ticker saham)"
    )
    open: float = Field(default=0.0)
    high: float = Field(default=0.0)
    low: float = Field(default=0.0)
    close: float = Field(default=0.0)
    volume: float = Field(default=0.0)

    class Settings:
        name = "stock_prices"
        timeseries = TimeSeriesConfig(
            time_field="timestamp",
            meta_field="metadata",
            granularity=Granularity.hours,
        )

    @property
    def ticker(self) -> str:
        return self.metadata.ticker

    @property
    def date(self) -> datetime.date:
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

Base = Document
