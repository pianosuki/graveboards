import json

from api import v1 as api
from app import db
from app.osu_api import OsuAPIClient
from app.database.schemas import RequestSchema


def search(**kwargs):
    kwargs.pop("user")
    kwargs.pop("token_info")

    request_filter = json.loads(kwargs.pop("request_filter")) if "request_filter" in kwargs else {}

    if "user_id" in request_filter:
        kwargs["user_id"] = request_filter["user_id"]["eq"]

    with db.session_scope() as session:
        requests = db.get_requests(**kwargs)
        requests_data = RequestSchema(many=True).dump(requests)

    return requests_data, 200


def post(body: dict):
    with db.session_scope() as session:
        errors = RequestSchema(session=session).validate(body)

    if errors:
        return {"error_type": "validation_error", "message": "Invalid input data", "errors": errors}, 400

    beatmapset_id = body["beatmapset_id"]

    if db.get_request(beatmapset_id=beatmapset_id):
        return {"error_type": "already_requested", "message": f"The request with beatmapset ID '{beatmapset_id}' already exists"}, 409

    oac = OsuAPIClient()
    beatmapset = oac.get_beatmapset(beatmapset_id)

    if beatmapset["status"] in ("ranked", "approved", "qualified", "loved"):
        return {"error_type": "already_ranked", "message": f"The beatmapset is already {beatmapset['status']} on osu!"}, 400

    api.beatmapsets.post({"beatmapset_id": beatmapset_id})

    db.add_request(**body)

    return {"message": "Request submitted successfully!"}, 201


def patch(request_id: int, body: dict):
    db.update_request(request_id, **body)

    return {"message": "Request updated successfully!"}, 200
