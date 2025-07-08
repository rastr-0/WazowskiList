from fastapi import FastAPI
# database + redis
from app.database.database import motor_db
from app.config.redis import redis
from contextlib import asynccontextmanager
# routers
from app.routers.auth import router as auth_router
from app.routers.task import router as task_router
from app.routers.reminder import router as remind_router
# logging
from app.logs.logging_config import setup_logging, LOGGING_CONFIG
# custom exception for logger
from app.exceptions.custom_exceptions import LoggingSetupException

# setup logging
try:
    setup_logging(log_config=LOGGING_CONFIG)
except Exception as e:
    raise LoggingSetupException()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    Code before `yield`:
        sets up database before actually starting taking requests
    Code after `yield`:
        cleans up the database right after the shutdown of the app
    """
    await motor_db.connect_and_init_db()
    await redis.connect_and_init_db()
    yield
    await motor_db.close_db_connection()
    await redis.close_connection()


app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(task_router)
app.include_router(remind_router)
