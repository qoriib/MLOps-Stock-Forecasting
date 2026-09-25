import os
import datetime
from typing import List, Dict, Any, Optional
import pandas as pd
from sqlalchemy import (
    create_engine,
    Column,
    String,
    Float,
    Integer,
    Date,
    DateTime,
    Boolean,
    Index,
)
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.dialects.postgresql import insert as pg_insert
from src import config

DATABASE_URL = config.DATABASE_URL

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


class ModelMetric(Base):
    __tablename__ = "model_metrics"

    ticker = Column(String(20), primary_key=True)
    model_name = Column(String(20), primary_key=True)  # LSTM / GRU
    mse = Column(Float, nullable=False)
    rmse = Column(Float, nullable=False)
    mape = Column(Float, nullable=False)
    r2 = Column(Float, nullable=False, default=0.0)
    time_steps = Column(Integer, nullable=False)
    optimizer = Column(String(20), nullable=False)
    batch_size = Column(Integer, nullable=False)
    learning_rate = Column(Float, nullable=False)
    is_best = Column(Boolean, nullable=False, default=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


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
    """Membuat tabel stock_prices dan model_metrics jika belum ada."""
    engine = get_engine()
    Base.metadata.create_all(bind=engine)


def upsert_stock_prices(df: pd.DataFrame, ticker: str) -> int:
    """Melakukan upsert data historis saham ke PostgreSQL tanpa redundansi."""
    if df.empty:
        return 0

    init_db()
    engine = get_engine()

    records = []
    for _, row in df.iterrows():
        d_val = pd.to_datetime(row["date"]).date()
        records.append({
            "ticker": ticker.strip().upper(),
            "date": d_val,
            "open": float(row.get("open", 0.0)),
            "high": float(row.get("high", 0.0)),
            "low": float(row.get("low", 0.0)),
            "close": float(row.get("close", 0.0)),
            "volume": float(row.get("volume", 0.0)),
        })

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


def upsert_model_metrics(
    ticker: str,
    metrics_summary: Dict[str, Any],
    best_overall_model: str,
) -> None:
    """Melakukan upsert ringkasan metrik model terbaik per ticker ke PostgreSQL."""
    init_db()
    engine = get_engine()

    records = []
    clean_ticker = ticker.strip().upper()

    for m_name, met in metrics_summary.items():
        is_best = (m_name.upper() == best_overall_model.upper())
        records.append({
            "ticker": clean_ticker,
            "model_name": m_name.upper(),
            "mse": float(met["MSE"]),
            "rmse": float(met["RMSE"]),
            "mape": float(met["MAPE"]),
            "r2": float(met.get("R2", 0.0)),
            "time_steps": int(met["time_steps"]),
            "optimizer": str(met["optimizer"]),
            "batch_size": int(met["batch_size"]),
            "learning_rate": float(met["learning_rate"]),
            "is_best": is_best,
            "updated_at": datetime.datetime.utcnow(),
        })

    if not records:
        return

    stmt = pg_insert(ModelMetric).values(records)
    upsert_stmt = stmt.on_conflict_do_update(
        index_elements=["ticker", "model_name"],
        set_={
            "mse": stmt.excluded.mse,
            "rmse": stmt.excluded.rmse,
            "mape": stmt.excluded.mape,
            "r2": stmt.excluded.r2,
            "time_steps": stmt.excluded.time_steps,
            "optimizer": stmt.excluded.optimizer,
            "batch_size": stmt.excluded.batch_size,
            "learning_rate": stmt.excluded.learning_rate,
            "is_best": stmt.excluded.is_best,
            "updated_at": stmt.excluded.updated_at,
        }
    )

    with engine.begin() as conn:
        conn.execute(upsert_stmt)
