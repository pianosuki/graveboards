import secrets

from app import db

API_KEY_LENGTH = 32


def generate_api_key() -> str:
    sequence = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return "".join(secrets.choice(sequence) for _ in range(API_KEY_LENGTH))


def validate_api_key(api_key: str) -> dict[str, int]:
    info = db.get_api_key(key=api_key)

    if not info:
        raise ValueError("Invalid API key")

    return {
        "sub": info.user_id,
        "iat": int(info.created_at.timestamp())
    }
