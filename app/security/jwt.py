from datetime import timedelta
from typing import Any

import jwt

from app.utils import aware_utcnow
from app.config import FRONTEND_BASE_URL, JWT_SECRET_KEY, JWT_ALGORITHM

JWT_LIFETIME_DAYS = 30


def generate_token(user_id):
    payload = {
        "sub": user_id,
        "iss": FRONTEND_BASE_URL,
        "iat": aware_utcnow(),
        "exp": aware_utcnow() + timedelta(days=JWT_LIFETIME_DAYS)
    }

    return encode_token(payload)


def encode_token(payload: dict[str, Any]) -> str:
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])


def validate_token(token: str) -> dict[str, int]:
    try:
        payload = decode_token(token)

        if payload["iss"] != FRONTEND_BASE_URL:
            raise jwt.InvalidIssuerError("Invalid token issuer")

        return payload

    except jwt.ExpiredSignatureError:
        raise

    except jwt.InvalidTokenError:
        raise
