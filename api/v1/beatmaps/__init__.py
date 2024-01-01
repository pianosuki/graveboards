import httpx
from flask import request, abort
from app import bm, cr
from app.schemas import beatmaps_schema, beatmap_schema


def search():
    beatmaps = cr.get_beatmaps()
    return beatmaps_schema.dump(beatmaps), 200


def get(beatmap_id: int):
    beatmap = cr.get_beatmap(id=beatmap_id)
    return beatmap_schema.dump(beatmap), 200


def post():
    beatmap_id = request.json["beatmap_id"]
    try:
        bm.download(beatmap_id)
    except httpx.HTTPStatusError as e:
        abort(e.response.status_code, e.response.json())
