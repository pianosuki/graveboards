from contextlib import asynccontextmanager, AbstractAsyncContextManager

from sqlalchemy import event
from sqlalchemy.sql import select
from sqlalchemy.pool.base import ConnectionPoolEntry
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine, AsyncSession
from sqlalchemy.engine import URL
from sqlalchemy.exc import SQLAlchemyError
from asyncpg.connection import Connection

from app.config import POSTGRESQL_CONFIGURATION
from .crud import CRUD
from . import events

DATABASE_URI = URL.create(**POSTGRESQL_CONFIGURATION)


class PostgresqlDB(CRUD):
    def __init__(self):
        self.engine: AsyncEngine = create_async_engine(DATABASE_URI)

        @event.listens_for(self.engine.sync_engine, "first_connect")
        def on_connect(dbapi_connection: Connection, connection_record: ConnectionPoolEntry):
            print(f"[{self.__class__.__name__}] Connected to PostgreSQL at '{DATABASE_URI}'")

    def async_session_generator(self) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(self.engine, expire_on_commit=False)

    async def close(self):
        await self.engine.dispose()

    async def test_connection(self):
        try:
            async with self.engine.connect() as conn:
                await conn.execute(select(1))

        except SQLAlchemyError:
            raise
        finally:
            await self.close()

    @asynccontextmanager
    async def session(self) -> AbstractAsyncContextManager[AsyncSession, None]:
        new_async_session = self.async_session_generator()

        async with new_async_session() as session_:
            try:
                yield session_
                await session_.commit()
            except Exception as e:
                await session_.rollback()
                raise e
            finally:
                await session_.close()
