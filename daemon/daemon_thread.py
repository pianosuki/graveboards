import asyncio
from threading import Thread
from traceback import print_exc

from .graveboards_daemon import GraveboardsDaemon


class DaemonThread(Thread):
    def __init__(self, daemon_app: "GraveboardsDaemon"):
        super().__init__(daemon=True)

        self._daemon_app = daemon_app
        self._loop = None

    def run(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        try:
            self._loop.run_until_complete(self._daemon_app.run())
        except Exception as e:
            print(f"[{self.__class__.__name__}] ERROR:", type(e).__name__, e)
            print_exc()
        finally:
            self._loop.close()
