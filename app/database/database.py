from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings
from app.logs.logging_config import database_logger
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pymongo.errors import OperationFailure


class Database:
    def __init__(self):
        self.db_client: AsyncIOMotorClient = None

    async def connect_and_init_db(self):
        """Establish a connection to the MongoDB server and initialize the database"""
        mongo_url = f"mongodb://{settings.MONGO_HOST}:{settings.MONGO_PORT}"

        try:
            self.db_client = AsyncIOMotorClient(mongo_url, uuidRepresentation="standard")
            database_logger.info("Mongo connection established")

            # Initialize the database and create a user if it doesn't exist
            db = self.db_client[settings.MONGO_DB]

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
            self.db_client = AsyncIOMotorClient(authenticated_mongo_url, uuidRepresentation="standard")

        except OperationFailure as e:
            database_logger.error(f"Failed to create or authenticate user: {str(e)}")
            raise
        except Exception as e:
            database_logger.error(f"Failed to connect to the database: {str(e)}")
            raise

    async def get_database(self) -> AsyncIOMotorDatabase:
        """Retrieve the active database instance"""
        if self.db_client is None:
            database_logger.error("Database client is not initialized")
            raise RuntimeError("Database client is not initialized")
        return self.db_client.get_database()

    async def close_db_connection(self):
        """Close a connection with the MongoDB server"""
        if self.db_client is None:
            database_logger.warning("Connection is None, nothing to close")
            return
        self.db_client.close()
        self.db_client = None
        database_logger.info("Mongo connection closed")


motor_db = Database()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    Code before `yield`:
        sets up database before actually starting taking requests
    Code after `yield`:
        cleans up the database right after the shutdown of the app
    """
    await motor_db.connect_and_init_db()
    yield
    await motor_db.close_db_connection()
