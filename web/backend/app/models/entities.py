import datetime
from typing import Any, Dict
from sqlalchemy import Date, Float, Index, String
from sqlalchemy.orm import Mapped, declarative_base, mapped_column

Base = declarative_base()

class StockPrice(Base):
    __tablename__ = "stock_prices"

    ticker: Mapped[str] = mapped_column(String(20), primary_key=True)
    date: Mapped[datetime.date] = mapped_column(Date, primary_key=True)
    open: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    high: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    low: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    close: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    volume: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    __table_args__ = (
        Index("idx_stock_prices_ticker_date", "ticker", "date"),
    )

    def to_dict(self) -> Dict[str, Any]:
        formatted_date = None
        if self.date is not None:
            formatted_date = self.date.strftime("%Y-%m-%d")

        price_dictionary = {
            "ticker": self.ticker,
            "date": formatted_date,
            "open": float(self.open),
            "high": float(self.high),
            "low": float(self.low),
            "close": float(self.close),
            "volume": float(self.volume),
        }
        return price_dictionary

    def __repr__(self) -> str:
        representation_string = f"<StockPrice(ticker='{self.ticker}', date='{self.date}', close={self.close})>"
        return representation_string
