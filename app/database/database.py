from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings
from app.logs.logging_config import database_logger
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pymongo.errors import OperationFailure

# TODO: Reorganize database logic to one class

db_client: AsyncIOMotorClient = None


async def get_database() -> AsyncIOMotorDatabase:
    return db_client.get_database()


async def connect_and_init_db():
    global db_client
    mongo_url = f"mongodb://{settings.MONGO_HOST}:{settings.MONGO_PORT}"

    try:
        db_client = AsyncIOMotorClient(mongo_url, uuidRepresentation="standard")
        database_logger.info("Mongo connection established")

        # Initialize the database and create a user if it doesn't exist
        db = db_client[settings.MONGO_DB]

        # Check if user exists
        existing_user = await db.command("usersInfo", settings.MONGO_USERNAME)
        if existing_user['users']:
            database_logger.info(f"User {settings.MONGO_USERNAME} already exists.")
        else:
            # Create a new user
            await db.command(
                "createUser", settings.MONGO_USERNAME,
                pwd=settings.MONGO_PASSWORD,
                roles=[{"role": "readWrite", "db": settings.MONGO_DB}]
            )
            database_logger.info(f"User {settings.MONGO_USERNAME} created.")

        # Now switch to authenticated client
        authenticated_mongo_url = (f"mongodb://{settings.MONGO_USERNAME}:{settings.MONGO_PASSWORD}@"
                                   f"{settings.MONGO_HOST}:{settings.MONGO_PORT}/{settings.MONGO_DB}")
        db_client = AsyncIOMotorClient(authenticated_mongo_url, uuidRepresentation="standard")

    except OperationFailure as e:
        database_logger.error(f"Failed to create or authenticate user: {str(e)}")
        raise
    except Exception as e:
        database_logger.error(f"Failed to connect to the database: {str(e)}")
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
