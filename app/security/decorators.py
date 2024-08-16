from functools import wraps
from typing import Callable, Any

from connexion.exceptions import Forbidden

from app import db
from app.enums import RoleName


def authorization_required(required_role: RoleName = None, override: Callable[..., bool] = None):
    def user_has_required_role(user_id: int) -> bool:
        if required_role is not None:
            with db.session_scope() as session:
                user_roles = [RoleName(role.name) for role in db.get_user(id=user_id, session=session).roles]

        return required_role is None or required_role in user_roles

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                user_id = kwargs["user"]
            except KeyError:
                func_path = ".".join((func.__module__, func.__name__))
                raise KeyError(f"Decorated function '{func_path}' must accept **kwargs")

            if not (
                (override is None and user_has_required_role(user_id)) or
                (override is not None and (override(*args, **kwargs) or user_has_required_role(user_id)))
            ):
                raise Forbidden(detail="User does not have permission to access this resource")

            return func(*args, **kwargs)

        return wrapper

    return decorator
