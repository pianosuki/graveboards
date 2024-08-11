from app import db


def api_key_info(apikey: str, required_scopes: list | None) -> dict | None:
    info = db.get_api_key(key=apikey)

    if not info:
        return None

    return {"uid": info.user_id}
