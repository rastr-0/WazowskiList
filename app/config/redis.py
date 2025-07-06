from aioredis import Redis, from_url
from app.logs.logging_config import message_broker_logger
from app.exceptions.custom_exceptions import CreateConnectionException


class MessageBroker:
    def __init__(self):
        self.broker: Redis = None

    async def connect_and_init_db(self):
        """Establish a connection to Redis and initialize"""
        redis_url = "redis://redis:6379/0"

        try:
            message_broker_logger.info("New Redis connection was successfully established")
            self.broker = await from_url(redis_url, decode_responses=True)
        except Exception as e:
            message_broker_logger.error(f"New Redis connection was not established: {e}")
            raise CreateConnectionException("Failed to establish connection with Redis")

    async def get_redis(self) -> Redis:
        if self.broker is None:
            raise RuntimeError("Redis is not initialized")
        return self.broker

    async def close_connection(self):
        if self.broker is not None:
            await self.broker.close()


redis = MessageBroker()
