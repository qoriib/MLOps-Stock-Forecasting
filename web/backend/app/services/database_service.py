import logging
from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from app.config import DATABASE_URL
from app.models.entities import Base

logger = logging.getLogger("database_service")

global_database_engine = None
global_session_factory = None

class DatabaseService:
    @staticmethod
    def get_connection_url() -> str:
        database_url = DATABASE_URL
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql+psycopg2://", 1)
        elif database_url.startswith("postgresql://") and not database_url.startswith("postgresql+"):
            database_url = database_url.replace("postgresql://", "postgresql+psycopg2://", 1)
        return database_url

    @classmethod
    def get_engine(cls):
        global global_database_engine
        if global_database_engine is None:
            connection_url = cls.get_connection_url()
            global_database_engine = create_engine(
                connection_url,
                pool_pre_ping=True,
                pool_recycle=1800,
                pool_size=10,
                max_overflow=20,
            )
        return global_database_engine

    @classmethod
    def get_session_factory(cls) -> sessionmaker:
        global global_session_factory
        if global_session_factory is None:
            database_engine = cls.get_engine()
            global_session_factory = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=database_engine,
                expire_on_commit=False,
            )
        return global_session_factory

    @classmethod
    def get_session(cls) -> Session:
        session_factory = cls.get_session_factory()
        session_instance = session_factory()
        return session_instance

    @classmethod
    @contextmanager
    def session_scope(cls) -> Generator[Session, None, None]:
        session_instance = cls.get_session()
        try:
            yield session_instance
            session_instance.commit()
        except Exception:
            session_instance.rollback()
            raise
        finally:
            session_instance.close()

    @classmethod
    def init_db(cls) -> None:
        database_engine = cls.get_engine()
        Base.metadata.create_all(bind=database_engine)
