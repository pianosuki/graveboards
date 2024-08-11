from sqlalchemy import select

from app.database.models import ModelClass, Base
from .decorators import session_manager, ensure_required
from .protocol import DatabaseProtocol
from .c import C
from .r import R
from .u import U
from .d import D


class CRUD(C, R, U, D, DatabaseProtocol):
    def create_database(self):
        with self.engine.begin() as conn:
            Base.metadata.create_all(conn)

    def recreate_database(self):
        with self.engine.begin() as conn:
            Base.metadata.drop_all(conn)
            Base.metadata.create_all(conn)

    def is_empty(self) -> bool:
        with self.session_scope() as session:
            for model_class in ModelClass:
                stmt = select(model_class.value).limit(1)
                result = session.execute(stmt)

                if result.scalars().first() is not None:
                    return False

        return True
