import httpx

from flask import abort

from app import bm, cr
from app.schemas import beatmapsets_schema
from . import listings, snapshots


def search(**kwargs):
    # To-do: handle filtering
    beatmapsets = cr.get_beatmapsets()
    return beatmapsets_schema.dump(beatmapsets), 200


def post(body: dict):
    beatmapset_id = body["beatmapset_id"]

    try:
        beatmap_ids = bm.archive(beatmapset_id)

        if any(beatmap_ids):
            response = {}

            for beatmap_id in beatmap_ids:
                snapshot_number = cr.get_latest_beatmap_snapshot(beatmap_id).snapshot_number
                response[beatmap_id] = snapshot_number

            return response, 201
        else:
            return "The latest versions of all the beatmaps in the beatmapset have already been downloaded, no further action is needed", 200
    except httpx.HTTPStatusError as e:
        abort(e.response.status_code, e.response.json())
