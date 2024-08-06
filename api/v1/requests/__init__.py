import json

from flask import abort, jsonify

from api import v1 as api
from app import cr, oac
from app.schemas import requests_schema, request_schema


def search(**kwargs):
    kwargs.pop("user")
    kwargs.pop("token_info")
    
    request_filter = json.loads(kwargs.pop("request_filter")) if "request_filter" in kwargs else {}
    
    if "user_id" in request_filter:
        kwargs["user_id"] = request_filter["user_id"]["eq"]
    
    requests = cr.get_requests(**kwargs)
    return requests_schema.dump(requests), 200


def post(body: dict):
    errors = request_schema.validate(body)

    if errors:
        return jsonify({"error_type": "validation_error", "message": "Invalid input data"}), 400

    beatmapset_id = body["beatmapset_id"]

    if cr.get_request(beatmapset_id=beatmapset_id):
        return jsonify({"error_type": "already_requested", "message": f"The request with beatmapset ID '{beatmapset_id}' already exists"}), 409

    beatmapset = oac.get_beatmapset(beatmapset_id)

    if beatmapset["status"] in ("ranked", "approved", "qualified", "loved"):
        return jsonify({"error_type": "already_ranked", "message": f"The beatmapset is already {beatmapset['status']} on osu!"}), 400

    api.beatmapsets.post({"beatmapset_id": beatmapset_id})

    cr.add_request(body)

    return jsonify({"message": "Request submitted successfully!"}), 201


def patch(request_id: int, body: dict):
    cr.update_request(request_id, **body)

    return jsonify({"message": "Request successfully updated!"}), 200
