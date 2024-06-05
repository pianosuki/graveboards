from __future__ import annotations

from typing import TYPE_CHECKING

from flask import Flask

if TYPE_CHECKING:
    from .daemon import GraveboardsDaemon


class ThreadSynchronization:
    def __init__(self, app: Flask | None = None):
        self.app = app

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        self.app = app
        app.extensions["thread_synchronization"] = self

    @property
    def daemon(self) -> GraveboardsDaemon | None:
        return self.app.extensions.get("daemon")
