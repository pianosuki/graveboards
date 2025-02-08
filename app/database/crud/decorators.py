from functools import wraps
from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import ModelClass, BaseType
from .protocol import DatabaseProtocol


def session_manager(func: Callable):
    @wraps(func)
    async def wrapper(self: DatabaseProtocol, *args, **kwargs):
        ctx = None
        session = kwargs.get("session", None)

        if not session:
            ctx = self.session()
            session = await ctx.__aenter__()
            kwargs["session"] = session

        try:
            result = await func(self, *args, **kwargs)
        except Exception as e:
            if ctx:
                await ctx.__aexit__(type(e), e, e.__traceback__)

            raise e
        else:
            if ctx:
                await ctx.__aexit__(None, None, None)

            return result

    return wrapper


def ensure_required(func: Callable):
    @wraps(func)
    async def wrapper(model_class: ModelClass, session: AsyncSession, **kwargs) -> BaseType:
        required_columns = model_class.get_required_columns()
        missing_columns = [col for col in required_columns if col not in kwargs]

        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

        return await func(model_class, session, **kwargs)

    return wrapper
