import asyncio

from .services import ServiceClass, ServiceType


class GraveboardsDaemon:
    def __init__(self):
        self.services: dict[ServiceClass, ServiceType] = {}

    def register_service(self, service_class: ServiceClass):
        self.services[service_class] = service_class.value()

    async def run(self):
        await asyncio.gather(*self.service_task_generator())

    def service_task_generator(self):
        for service in self.services.values():
            yield asyncio.create_task(service.run())
