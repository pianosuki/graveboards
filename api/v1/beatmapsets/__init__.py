import httpx

from flask import abort

from app import bm, cr


def post(body: dict):
    beatmapset_id = body["beatmapset_id"]

    if cr.beatmapset_exists(beatmapset_id):
        abort(409, f"The beatmapset with ID '{beatmapset_id}' already exists")

    try:
        bm.download_set(beatmapset_id)
    except httpx.HTTPStatusError as e:
        abort(e.response.status_code, e.response.json())
