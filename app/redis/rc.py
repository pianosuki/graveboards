from contextlib import contextmanager

from redis import Redis
from redis.asyncio import Redis as AsyncRedis

from app.config import REDIS_CONFIGURATION

REDIS_BASE_URL = f"redis://{REDIS_CONFIGURATION["username"]}:***@{REDIS_CONFIGURATION["host"]}:{REDIS_CONFIGURATION["port"]}/{REDIS_CONFIGURATION["db"]}"


class RedisClient(AsyncRedis):
    def __init__(self):
        super().__init__(**REDIS_CONFIGURATION)
        print(f"[{self.__class__.__name__}] Connected to Redis at '{REDIS_BASE_URL}'")

    async def paginate_scan(self, pattern: str, limit: int = None, offset: int = 0, type_: str = None) -> list[str]:
        keys = []
        count = 0

        async for key in self.scan_iter(match=pattern, _type=type_):
            if count < offset:
                count += 1
                continue

            if limit is not None and len(keys) >= limit:
                break

            keys.append(key)

        return keys


@contextmanager
def redis_connection():
    from .pool import connection_pool

    rc = Redis(connection_pool=connection_pool)

    try:
        yield rc
    finally:
        rc.close()
