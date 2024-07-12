import httpx

from flask import abort

from app import bm, cr


def post(body: dict):
    beatmapset_id = body["beatmapset_id"]

    try:
        results = bm.download_set(beatmapset_id)

        if any(results.values()):
            response = {}

            for beatmap_id, result in results.items():
                if result:
                    version_number = cr.get_latest_beatmap_version(beatmap_id).version_number
                    response[beatmap_id] = version_number

            return response, 201
        else:
            return "The latest versions of all the beatmaps in the beatmapset have already been downloaded, no further action is needed", 200
    except httpx.HTTPStatusError as e:
        abort(e.response.status_code, e.response.json())
