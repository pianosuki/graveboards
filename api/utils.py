def pop_auth_info(kwargs: dict) -> dict:
    return {key: kwargs.pop(key) for key in ("user", "token_info") if key in kwargs}


def prime_query_kwargs(kwargs: dict) -> dict:
    for key, value in list(kwargs.items()):
        match key:
            case "limit" | "offset" | "reversed":
                kwargs["_" + key] = kwargs.pop(key)

    return pop_auth_info(kwargs)
