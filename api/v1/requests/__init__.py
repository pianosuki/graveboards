import json

from api.utils import prime_query_kwargs
from app import db, rc
from app.osu_api import OsuAPIClient
from app.database.schemas import RequestSchema
from app.security import role_authorization
from app.enums import RoleName
from app.redis import Namespace, ChannelName
from app.redis.models import QueueRequestHandlerTask
from app.config import ADMIN_USER_IDS


def search(**kwargs):
    requester_user_id = kwargs["user"]
    prime_query_kwargs(kwargs)
    request_filter = json.loads(kwargs.pop("request_filter")) if "request_filter" in kwargs else {}

    if "user_id" in request_filter:
        requested_user_id = request_filter["user_id"]["eq"]

        if not requester_user_id == requested_user_id and requester_user_id not in ADMIN_USER_IDS:
            return {"message": f"You are not authorized to access this resource"}, 403

        kwargs["user_id"] = requested_user_id

    with db.session_scope() as session:
        requests = db.get_requests(session=session, **kwargs)
        requests_data = RequestSchema(many=True, session=session).dump(requests)

    return requests_data, 200


def get(request_id: int):
    with db.session_scope() as session:
        request = db.get_request(id=request_id, session=session)
        request_data = RequestSchema(session=session).dump(request)

    return request_data, 200


def post(body: dict, **kwargs):
    with db.session_scope() as session:
        errors = RequestSchema(session=session).validate(body)

    if errors:
        return {"message": "Invalid input data", "errors": errors}, 400

    beatmapset_id = body["beatmapset_id"]
    queue_id = body["queue_id"]
    queue_name = db.get_queue(id=queue_id).name

    if db.get_request(beatmapset_id=beatmapset_id, queue_id=queue_id):
        return {"message": f"The request with beatmapset ID '{beatmapset_id}' already exists in queue '{queue_name}'"}, 409

    oac = OsuAPIClient()
    beatmapset_dict = oac.get_beatmapset(beatmapset_id)

    if beatmapset_dict["status"] in ("ranked", "approved", "qualified", "loved"):
        return {"message": f"The beatmapset is already {beatmapset_dict['status']} on osu!"}, 400

    task = QueueRequestHandlerTask(**body)
    task_hash_name = Namespace.QUEUE_REQUEST_HANDLER_TASK.hash_name(task.hashed_id)

    if rc.exists(task_hash_name):
        return {"message": f"The request with beatmapset ID '{beatmapset_id}' in queue '{queue_name}' is currently being processed"}, 409

    rc.hset(task_hash_name, mapping=task.serialize())
    rc.publish(ChannelName.QUEUE_REQUEST_HANDLER_TASKS.value, task.hashed_id)

    return {"message": "Request submitted and queued for processing!", "task_id": task.hashed_id}, 202


@role_authorization(RoleName.ADMIN)
def patch(request_id: int, body: dict, **kwargs):
    db.update_request(request_id, **body)

    return {"message": "Request updated successfully!"}, 200
