import httpx

from flask import abort

from app import bm, cr
from app.schemas import beatmaps_schema, beatmap_schema


def search():
    beatmaps = cr.get_beatmaps()
    return beatmaps_schema.dump(beatmaps), 200


def get(beatmap_id: int):
    beatmap = cr.get_beatmap(id=beatmap_id)
    return beatmap_schema.dump(beatmap), 200


def post(body: dict):
    beatmap_id = body["beatmap_id"]

    if cr.beatmap_exists(beatmap_id):
        abort(409, f"The beatmap with ID '{beatmap_id}' already exists")

    try:
        bm.download(beatmap_id)
    except httpx.HTTPStatusError as e:
        abort(e.response.status_code, e.response.json())
