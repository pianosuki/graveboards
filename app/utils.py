import time
import uuid
import secrets
import hashlib
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


def parse_iso8601(datetime_string) -> datetime:
    if datetime_string.endswith("Z"):
        return datetime.strptime(datetime_string, "%Y-%m-%dT%H:%M:%S%z")
    elif "+" in datetime_string:
        return datetime.strptime(datetime_string, "%Y-%m-%dT%H:%M:%S%z")
    else:
        return datetime.strptime(datetime_string, "%Y-%m-%dT%H:%M:%S")


def combine_checksums(checksums: list[str]) -> str:
    combined_hash = hashlib.md5()

    for checksum in checksums:
        combined_hash.update(checksum.encode())

    return combined_hash.hexdigest()
