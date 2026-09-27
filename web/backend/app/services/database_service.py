import logging
from typing import Optional
from beanie import init_beanie
from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase
from app.config import MONGODB_DB_NAME, MONGODB_URL
from app.models.entities import StockPrice

logger = logging.getLogger("database_service")

global_mongo_client: Optional[AsyncMongoClient] = None
global_mongo_db: Optional[AsyncDatabase] = None

class DatabaseService:
    @classmethod
    async def init_db(cls) -> None:
        global global_mongo_client, global_mongo_db
        if global_mongo_client is None:
            connection_url = MONGODB_URL
            logger.info("Menghubungkan ke MongoDB...")
            global_mongo_client = AsyncMongoClient(
                connection_url,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
            )
            
            global_mongo_db = global_mongo_client[MONGODB_DB_NAME]
            
            await init_beanie(
                database=global_mongo_db,
                document_models=[StockPrice],
            )
            logger.info(f"Beanie ODM terhubung ke database MongoDB '{MONGODB_DB_NAME}'.")

    @classmethod
    async def close_db(cls) -> None:
        global global_mongo_client, global_mongo_db
        if global_mongo_client is not None:
            await global_mongo_client.close()
            global_mongo_client = None
            global_mongo_db = None
            logger.info("Koneksi MongoDB berhasil ditutup.")

    @classmethod
    async def ensure_initialized(cls) -> None:
        if global_mongo_client is None:
            await cls.init_db()

    @classmethod
    def get_client(cls) -> Optional[AsyncMongoClient]:
        return global_mongo_client

    @classmethod
    def get_database(cls) -> Optional[AsyncDatabase]:
        return global_mongo_db
