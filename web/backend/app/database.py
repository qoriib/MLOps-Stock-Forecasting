import os
import datetime
import logging
from typing import List, Optional
import pandas as pd
from sqlalchemy import (
    create_engine,
    Column,
    String,
    Float,
    Date,
    Index,
    select,
)
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.dialects.postgresql import insert as pg_insert

logger = logging.getLogger("backend_database")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/stock_db"
)

Base = declarative_base()


class StockPrice(Base):
    __tablename__ = "stock_prices"

    ticker = Column(String(20), primary_key=True)
    date = Column(Date, primary_key=True)
    open = Column(Float, nullable=False, default=0.0)
    high = Column(Float, nullable=False, default=0.0)
    low = Column(Float, nullable=False, default=0.0)
    close = Column(Float, nullable=False, default=0.0)
    volume = Column(Float, nullable=False, default=0.0)

    __table_args__ = (
        Index("idx_stock_prices_ticker_date", "ticker", "date"),
    )


_engine = None
_SessionLocal = None


def get_engine():
    global _engine
    if _engine is None:
        db_url = os.getenv("DATABASE_URL", DATABASE_URL)
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        _engine = create_engine(db_url, pool_pre_ping=True)
    return _engine


def get_db_session():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal()


def init_db():
    """Membuat tabel stock_prices di PostgreSQL jika belum ada."""
    engine = get_engine()
    Base.metadata.create_all(bind=engine)


def upsert_stock_prices(df: pd.DataFrame, ticker: str) -> int:
    """Melakukan upsert data historis saham ke PostgreSQL sebagai cache on-demand."""
    if df is None or df.empty:
        return 0

    init_db()
    engine = get_engine()

    records = []
    clean_ticker = ticker.strip().upper()
    for _, row in df.iterrows():
        d_val = pd.to_datetime(row["date"]).date()
        records.append({
            "ticker": clean_ticker,
            "date": d_val,
            "open": float(row.get("open", 0.0)),
            "high": float(row.get("high", 0.0)),
            "low": float(row.get("low", 0.0)),
            "close": float(row.get("close", 0.0)),
            "volume": float(row.get("volume", 0.0)),
        })

    if not records:
        return 0

    stmt = pg_insert(StockPrice).values(records)
    upsert_stmt = stmt.on_conflict_do_update(
        index_elements=["ticker", "date"],
        set_={
            "open": stmt.excluded.open,
            "high": stmt.excluded.high,
            "low": stmt.excluded.low,
            "close": stmt.excluded.close,
            "volume": stmt.excluded.volume,
        }
    )

    with engine.begin() as conn:
        conn.execute(upsert_stmt)

    return len(records)
