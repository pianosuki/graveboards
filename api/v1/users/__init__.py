from flask import abort, jsonify

from app import cr, sync, oac
from app.models import User
from app.schemas import users_schema
from app.services import ServiceName, QueueName


def search():
    users = User.query.all()
    return users_schema.dump(users), 200


def get(user_id: int):
    user_profile = oac.get_user(user_id)
    return jsonify(user_profile)


def post(body: dict):
    user_id = body["user_id"]

    if cr.user_exists(user_id):
        abort(409, f"The user with ID '{user_id}' already exists")
    else:
        cr.add_user(user_id)

    score_fetcher_task = cr.get_score_fetcher_task(user_id=user_id)

    if not score_fetcher_task:
        task = cr.add_score_fetcher_task(user_id)
        sync.daemon.services[ServiceName.SCORE_FETCHER].queues[QueueName.SCORE_FETCHER_TASKS].put(task.id)
