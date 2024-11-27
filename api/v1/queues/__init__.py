from api.utils import prime_query_kwargs
from app import db
from app.database.schemas import QueueSchema
from app.security import authorization_required
from app.enums import RoleName


def search(**kwargs):
    prime_query_kwargs(kwargs)

    with db.session_scope() as session:
        queues = db.get_queues(session=session, **kwargs)
        queues_data = QueueSchema(many=True, session=session).dump(queues)

    return queues_data, 200


def get(queue_id: int):
    with db.session_scope() as session:
        queue = db.get_queue(id=queue_id, session=session)
        queue_data = QueueSchema(session=session).dump(queue)

    return queue_data, 200


@authorization_required(RoleName.ADMIN)
def post(body: dict, **kwargs):  # TODO: Allow users to post queues for their user_id when we're ready for that feature
    with db.session_scope() as session:
        errors = QueueSchema(session=session).validate(body)

    if errors:
        return {"error_type": "validation_error", "message": "Invalid input data", "errors": errors}, 400

    user_id = body["user_id"]

    db.add_queue(user_id=user_id)

    return {"message": "Queue added successfully!"}, 201
