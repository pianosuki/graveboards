from redis import Redis
from redis.asyncio import Redis as AsyncRedis

from app.config import REDIS_CONFIGURATION
from .enums import ChannelName, Namespace

__all__ = [
    "RedisClient",
    "AsyncRedisClient",
    "ChannelName",
    "Namespace"
]

REDIS_BASE_URL = f"redis://{REDIS_CONFIGURATION["username"]}:***@{REDIS_CONFIGURATION["host"]}:{REDIS_CONFIGURATION["port"]}/{REDIS_CONFIGURATION["db"]}"


class RedisClientBase:
    def __init__(self):
        super().__init__(**REDIS_CONFIGURATION)

        print(f"[{self.__class__.__name__}] Connected to Redis at '{REDIS_BASE_URL}'")


class RedisClient(RedisClientBase, Redis):
    pass


class AsyncRedisClient(RedisClientBase, AsyncRedis):
    pass
