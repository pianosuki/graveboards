import time
import uuid
import secrets
from datetime import datetime, timezone


def generate_nonce() -> str:
    timestamp = int(time.time())
    random_string = generate_uuid()
    return f"{timestamp}-{random_string}"


def generate_uuid() -> str:
    return uuid.uuid4().hex


def generate_token(length: int) -> str:
    sequence = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return ''.join(secrets.choice(sequence) for _ in range(length))


def aware_utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)
