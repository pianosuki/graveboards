from app import db
from app.database.schemas import QueueSchema


def search(**kwargs):
    with db.session_scope() as session:
        queues = db.get_queues(session=session)
        queues_data = QueueSchema(many=True).dump(queues)

    return queues_data, 200


def get(queue_id: int):
    with db.session_scope() as session:
        queue = db.get_queue(id=queue_id, session=session)
        queue_data = QueueSchema().dump(queue)

    return queue_data, 200


def post(body: dict):
    errors = QueueSchema().validate(body)

    if errors:
        return {"error_type": "validation_error", "message": "Invalid input data", "errors": errors}, 400

    user_id = body["user_id"]

    db.add_queue(user_id=user_id)

    return {"message": "Queue added successfully!"}, 201
