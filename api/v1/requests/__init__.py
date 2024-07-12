from flask import abort

from api import v1 as api
from app import cr
from app.schemas import requests_schema


def search(**kwargs):
    # To-do: handle filtering
    requests = cr.get_requests()
    return requests_schema.dump(requests), 200


def post(body: dict):
    beatmapset_id = body.get("beatmapset_id")

    api.beatmapsets.post({"beatmapset_id": beatmapset_id})

    if cr.get_request(beatmapset_id=beatmapset_id):
        abort(409, f"The request with beatmapset ID '{beatmapset_id}' already exists")

    cr.add_request(body)
