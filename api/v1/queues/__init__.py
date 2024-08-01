from flask import abort

from app import cr
from app.schemas import queues_schema, queue_schema


def search(**kwargs):
    queues = cr.get_queues()
    return queues_schema.dump(queues), 200


def get(queue_id: int):
    queue = cr.get_queue(id=queue_id)
    return queue_schema.dump(queue), 200


def post(body: dict):
    print(body)
    errors = queue_schema.validate(body)

    if errors:
        abort(400, "Invalid input data")

    user_id = body["user_id"]

    cr.add_queue(user_id=user_id)
