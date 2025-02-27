import asyncio
import logging

from app.redis import RedisClient
from app.database import PostgresqlDB
from .services import ServiceClass, ServiceType

logger = logging.getLogger("daemon")


class ServiceDaemon:
    def __init__(self, rc: RedisClient, db: PostgresqlDB):
        self.rc = rc
        self.db = db

        self.services: dict[ServiceClass, ServiceType] = {}
        self.service_tasks: dict[ServiceClass, asyncio.Task] = {}

    async def run(self):
        self.service_tasks = {
            service_class: asyncio.create_task(service.run(), name=f"Service-{service_class.name}")
            for service_class, service in self.services.items()
        }

        logger.info(f"Loaded services: ({len(self.services)})")

        try:
            await asyncio.gather(*self.service_tasks.values())
        except Exception as e:
            logger.exception("Daemon encountered an error:\n%s", e)
            raise

    def register_service(self, service_class: ServiceClass):
        self.services[service_class] = service_class.value(self.rc, self.db)

    async def shutdown(self):
        for task in self.service_tasks.values():
            task.cancel()

        for task in self.service_tasks.values():
            try:
                await task
            except asyncio.CancelledError:
                pass
