import httpx
import json

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

    try:
        result = bm.download_map(beatmap_id)

        if result:
            version_number = cr.get_latest_beatmap_version(beatmap_id).version_number
            return {beatmap_id: version_number}, 201
        else:
            return "The latest version of the beatmap has already been downloaded, no further action is needed", 200
    except httpx.HTTPStatusError as e:
        abort(e.response.status_code, e.response.json())
