from flask import Flask


class Service:
    def __init__(self, app: Flask):
        self.app = app

    def __await__(self):
        return self.run

    async def run(self):
        ...
