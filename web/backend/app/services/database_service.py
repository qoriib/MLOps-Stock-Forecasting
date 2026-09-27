import logging
from typing import Optional
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import MONGODB_DB_NAME, MONGODB_URL
from app.models.entities import StockPrice

logger = logging.getLogger("database_service")

global_motor_client: Optional[AsyncIOMotorClient] = None
global_mongo_db: Optional[AsyncIOMotorDatabase] = None

class DatabaseService:
    @classmethod
    async def init_db(cls) -> None:
        global global_motor_client, global_mongo_db
        if global_motor_client is None:
            connection_url = MONGODB_URL
            logger.info("Menghubungkan ke MongoDB...")
            global_motor_client = AsyncIOMotorClient(
                connection_url,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
            )
            global_mongo_db = global_motor_client[MONGODB_DB_NAME]
            await init_beanie(
                database=global_mongo_db,
                document_models=[StockPrice],
            )
            logger.info(f"Beanie ODM terhubung ke database MongoDB '{MONGODB_DB_NAME}'.")

    @classmethod
    async def close_db(cls) -> None:
        global global_motor_client, global_mongo_db
        if global_motor_client is not None:
            global_motor_client.close()
            global_motor_client = None
            global_mongo_db = None
            logger.info("Koneksi MongoDB berhasil ditutup.")

    @classmethod
    async def ensure_initialized(cls) -> None:
        if global_motor_client is None:
            await cls.init_db()

    @classmethod
    def get_client(cls) -> Optional[AsyncIOMotorClient]:
        return global_motor_client

    @classmethod
    def get_database(cls) -> Optional[AsyncIOMotorDatabase]:
        return global_mongo_db
