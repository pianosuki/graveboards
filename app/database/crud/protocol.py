from typing import Protocol
from contextlib import AbstractAsyncContextManager

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession


class DatabaseProtocol(Protocol):
    engine: AsyncEngine

    async def session(self) -> AbstractAsyncContextManager[AsyncSession, None]:
        ...
        yield AsyncSession()
        ...
