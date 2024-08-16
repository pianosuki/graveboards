class Service:
    def __await__(self):
        return self.run

    async def run(self):
        ...
