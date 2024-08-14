def matching_user_id_override(*args, **kwargs) -> bool:
    authenticated_user_id = kwargs["user"]
    resource_user_id = kwargs["user_id"]

    return authenticated_user_id == resource_user_id
