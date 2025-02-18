from typing import Iterable, Any
from copy import copy


def pop_auth_info(kwargs: dict[str, Any]) -> dict[str, Any]:
    return {key: kwargs.pop(key) for key in ("user", "token_info") if key in kwargs}


def prime_query_kwargs(kwargs: dict[str, Any]) -> dict[str, Any]:
    for key, value in list(kwargs.items()):
        match key:
            case "limit" | "offset" | "reversed":
                kwargs["_" + key] = kwargs.pop(key)

    return pop_auth_info(kwargs)


def bleach_body(body: dict[str, Any], whitelisted_keys: Iterable[str] = None, blacklisted_keys: Iterable[str] = None) -> dict[str, Any]:
    bleached_body = {key: body[key] for key in whitelisted_keys if key in body} if whitelisted_keys else copy(body)

    for key in blacklisted_keys:
        bleached_body.pop(key, None)

    return bleached_body
