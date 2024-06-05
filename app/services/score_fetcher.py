import asyncio

from flask import Flask
from .service import Service


class ScoreFetcher(Service):
    def __init__(self, app: Flask):
        super().__init__(app)

    async def run(self):
        pass
