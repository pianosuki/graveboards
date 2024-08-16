from typing import Protocol, ContextManager

from sqlalchemy.engine.base import Engine
from sqlalchemy.orm.session import Session

MIN_LIMIT = 1
MAX_LIMIT = 100
DEFAULT_LIMIT = 50


class DatabaseProtocol(Protocol):
    engine: Engine = ...

    def session_scope(self) -> ContextManager[Session]:
        ...
        yield Session()
        ...
