import json

from api import v1 as api
from api.utils import prime_query_kwargs
from app import db
from app.osu_api import OsuAPIClient
from app.database.schemas import RequestSchema
from app.security import role_authorization
from app.enums import RoleName
from app.config import PRIMARY_ADMIN_USER_ID, ADMIN_USER_IDS


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
        return {"error_type": "validation_error", "message": "Invalid input data", "errors": errors}, 400

    beatmapset_id = body["beatmapset_id"]
    queue_id = body["queue_id"]
    queue_name = db.get_queue(id=queue_id).name

    if db.get_request(beatmapset_id=beatmapset_id, queue_id=queue_id):
        return {"error_type": "already_requested", "message": f"The request with beatmapset ID '{beatmapset_id}' already exists in queue '{queue_name}'"}, 409

    oac = OsuAPIClient()
    beatmapset = oac.get_beatmapset(beatmapset_id)

    if beatmapset["status"] in ("ranked", "approved", "qualified", "loved"):
        return {"error_type": "already_ranked", "message": f"The beatmapset is already {beatmapset['status']} on osu!"}, 400

    api.beatmapsets.post({"beatmapset_id": beatmapset_id}, user=PRIMARY_ADMIN_USER_ID)

    db.add_request(**body)

    return {"message": "Request submitted successfully!"}, 201


@role_authorization(RoleName.ADMIN)
def patch(request_id: int, body: dict, **kwargs):
    db.update_request(request_id, **body)

    return {"message": "Request updated successfully!"}, 200
