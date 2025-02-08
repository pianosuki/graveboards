import asyncio
from functools import wraps
from typing import Callable, Any, Awaitable

from connexion import request
from connexion.exceptions import Forbidden

from app.database import PostgresqlDB
from app.enums import RoleName


def role_authorization(required_role: RoleName = None, override: Callable[..., bool] = None):
    def decorator(func: Callable[..., Awaitable[Any]]):
        if not asyncio.iscoroutinefunction(func):
            raise ValueError(f"Function '{func.__name__}' must be async to use @role_authorization")

        @wraps(func)
        async def wrapper(*args, **kwargs) -> Awaitable[Any]:
            db: PostgresqlDB = request.state.db

            try:
                user_id = kwargs["user"]
            except KeyError:
                func_path = ".".join((func.__module__, func.__name__))
                raise KeyError(f"Decorated function '{func_path}' must accept **kwargs to use @role_authorization")

            user_has_required_role = required_role in [
                RoleName(role.name) for role in (
                    await db.get_user(id=user_id, _eager_loads={"roles": "selectinload"})
                ).roles
            ] if required_role is not None else True

            if not (
                (override is None and user_has_required_role) or
                (override is not None and (override(*args, **kwargs) or user_has_required_role))
            ):
                raise Forbidden(detail="User does not have permission to access this resource")

            return await func(*args, **kwargs)

        return wrapper

    return decorator
