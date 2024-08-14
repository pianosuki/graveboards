from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import URL

from app.config import POSTGRESQL_CONFIGURATION
from .crud import CRUD
from .events import *

DATABASE_URI = URL.create(**POSTGRESQL_CONFIGURATION)


class PostgresqlDB(CRUD):
    def __init__(self):
        self.engine = create_engine(DATABASE_URI, echo=False)

    def session_generator(self):
        return sessionmaker(self.engine, expire_on_commit=False)

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        new_session = self.session_generator()

        with new_session() as session_:
            try:
                yield session_
                session_.commit()

            except Exception as e:
                session_.rollback()
                raise e

            finally:
                session_.close()
