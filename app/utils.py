import time, uuid, secrets
from sqlalchemy.orm.collections import InstrumentedList


def generate_nonce() -> str:
    timestamp = int(time.time())
    random_string = generate_uuid()
    return f"{timestamp}-{random_string}"


def generate_uuid() -> str:
    return uuid.uuid4().hex


def generate_token(length: int) -> str:
    sequence = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return ''.join(secrets.choice(sequence) for _ in range(length))


def convert_instrumentedlist_to_dict(input_list: InstrumentedList) -> dict:
    return {item.id: item for item in input_list}
