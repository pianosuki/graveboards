from functools import wraps
from typing import Callable

from sqlalchemy.orm import Session

from app.database.models import ModelClass, BaseType


def session_manager(func: Callable):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        ctx = None
        session = kwargs.get("session", None)

        if not session:
            ctx = self.session_scope()
            session = ctx.__enter__()
            kwargs["session"] = session

        try:
            result = func(self, *args, **kwargs)

        except Exception as e:
            if ctx:
                ctx.__exit__(type(e), e, e.__traceback__)

            raise e

        else:
            if ctx:
                ctx.__exit__(None, None, None)

            return result

    return wrapper


def ensure_required(func: Callable):
    @wraps(func)
    def wrapper(model_class: ModelClass, session: Session, **kwargs) -> BaseType:
        required_columns = model_class.get_required_columns()
        missing_columns = [col for col in required_columns if col not in kwargs]

        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

        return func(model_class, session, **kwargs)

    return wrapper
