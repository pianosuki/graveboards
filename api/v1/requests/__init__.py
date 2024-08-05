from flask import abort

from api import v1 as api
from app import cr, oac
from app.schemas import requests_schema, request_schema


def search(**kwargs):
    requests = cr.get_requests()
    return requests_schema.dump(requests), 200


def post(body: dict):
    errors = request_schema.validate(body)

    if errors:
        abort(400, "Invalid input data")

    beatmapset_id = body["beatmapset_id"]

    if cr.get_request(beatmapset_id=beatmapset_id):
        abort(409, f"The request with beatmapset ID '{beatmapset_id}' already exists")

    beatmapset = oac.get_beatmapset(beatmapset_id)

    if beatmapset["status"] in ("ranked", "approved", "qualified", "loved"):
        abort(400, f"The beatmapset is already {beatmapset["status"]} on osu!")

    api.beatmapsets.post({"beatmapset_id": beatmapset_id})

    cr.add_request(body)
