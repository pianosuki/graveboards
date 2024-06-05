import asyncio, threading, traceback
from flask import Flask
from .services.service import Service


class DaemonThread(threading.Thread):
    def __init__(self, daemon: "GraveboardsDaemon"):
        super().__init__(daemon=True)

        self.name = self.__class__.__name__

        self._daemon = daemon
        self._loop = None

    def run(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        try:
            self._loop.run_until_complete(self._daemon.run())
        except Exception as e:
            print(f"[{self.__class__.__name__}] ERROR:", type(e).__name__, e)
            traceback.print_exc()
        finally:
            self._loop.close()


class GraveboardsDaemon:
    def __init__(self, app: Flask | None = None):
        self.app = app
        self.services: list[Service] = []

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        self.app = app
        app.extensions["daemon"] = self

    def register_service(self, service_class: type[Service]):
        self.services.append(service_class(self.app))

    async def run(self):
        await asyncio.gather(*self.service_task_generator())

    def service_task_generator(self):
        for service in self.services:
            yield asyncio.create_task(service.run())
