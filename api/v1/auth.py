from jwt.exceptions import InvalidIssuerError, ExpiredSignatureError, InvalidTokenError

from app.security import validate_api_key, validate_token


def api_key_info(api_key: str) -> dict | None:
    try:
        return validate_api_key(api_key)

    except ValueError:
        return None


def bearer_info(token: str) -> dict | None:
    try:
        return validate_token(token)

    except (InvalidIssuerError, ExpiredSignatureError, InvalidTokenError):
        return None
