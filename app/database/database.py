from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings
from app.logs.logging_config import database_logger
from contextlib import asynccontextmanager
from fastapi import FastAPI

# TODO: Reorganize database logic to one class

db_client: AsyncIOMotorClient = None


async def get_database() -> AsyncIOMotorDatabase:
    return db_client.get_database()


async def connect_and_init_db():
    global db_client
    mongo_url = (f"mongodb://{settings.MONGO_USERNAME}:{settings.MONGO_PASSWORD}@"
                 f"{settings.MONGO_HOST}:{settings.MONGO_PORT}/{settings.MONGO_DB}")
    try:
        db_client = AsyncIOMotorClient(mongo_url, uuidRepresentation="standard")
        database_logger.info("Mongo connection established")
    except Exception as _:
        raise


async def close_db_connection():
    global db_client
    if db_client is None:
        database_logger.warning("Connection is None, nothing to close")
        return
    db_client.close()
    db_client = None
    database_logger.info("Mongo connection closed")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    Code before `yield`:
        sets up database before actually starting taking requests
    Code after `yield`:
        cleans up the database right after the shutdown of the app
    """
    await connect_and_init_db()
    yield
    await close_db_connection()
