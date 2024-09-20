import uuid
import hashlib
from datetime import datetime, timezone
from io import BytesIO


def generate_uuid() -> str:
    return uuid.uuid4().hex


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


async def stream_file(file: BytesIO, chunk_size: int = 1024):
    file.seek(0)

    while chunk := file.read(chunk_size):
        yield chunk
