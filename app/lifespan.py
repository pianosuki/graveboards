import asyncio
from contextlib import asynccontextmanager

from connexion.middleware import ConnexionMiddleware

from app.redis import RedisClient
from app.database import PostgresqlDB
from app.logger import logger
from app.config import DISABLE_SECURITY
from daemon.service_daemon import ServiceDaemon
from daemon.services import ServiceClass


@asynccontextmanager
async def lifespan(app: ConnexionMiddleware):
    if DISABLE_SECURITY:
        logger.warning("Security has been disabled!")

    rc = RedisClient()
    db = PostgresqlDB()

    daemon_app = ServiceDaemon(rc, db)
    daemon_app.register_service(ServiceClass.SCORE_FETCHER)
    daemon_app.register_service(ServiceClass.PROFILE_FETCHER)
    daemon_app.register_service(ServiceClass.QUEUE_REQUEST_HANDLER)

    task = asyncio.create_task(daemon_app.run(), name="Daemon Task")

    try:
        yield {"rc": rc, "db": db}
    finally:
        await daemon_app.shutdown()
        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            pass

        await rc.aclose()
        await db.close()

        from app.redis.pool import connection_pool
        connection_pool.close()
