from app import flask_app
from .models import ApiKey


def api_key_info(apikey: str, required_scopes: list | None) -> dict | None:
    with flask_app.app_context():
        info = ApiKey.query.filter_by(key=apikey).first()

    if not info:
        return None

    return {"uid": info.user_id}
