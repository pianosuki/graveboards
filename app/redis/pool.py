from redis import ConnectionPool

from app.config import REDIS_CONFIGURATION

connection_pool = ConnectionPool(**REDIS_CONFIGURATION)
