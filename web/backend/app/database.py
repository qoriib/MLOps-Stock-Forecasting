import os
import datetime
import logging
from typing import List, Optional, Dict, Any
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
    select,
)
from sqlalchemy.orm import declarative_base, sessionmaker

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


class ModelMetric(Base):
    __tablename__ = "model_metrics"

    ticker = Column(String(20), primary_key=True)
    model_name = Column(String(20), primary_key=True)
    mse = Column(Float, nullable=False)
    rmse = Column(Float, nullable=False)
    mape = Column(Float, nullable=False)
    r2 = Column(Float, nullable=False, default=0.0)
    time_steps = Column(Integer, nullable=False)
    optimizer = Column(String(20), nullable=False)
    batch_size = Column(Integer, nullable=False)
    learning_rate = Column(Float, nullable=False)
    is_best = Column(Boolean, nullable=False, default=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)


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
