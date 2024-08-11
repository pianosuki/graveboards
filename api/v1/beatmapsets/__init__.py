import httpx

from app import db
from app.beatmap_manager import BeatmapManager
from app.database.schemas import BeatmapsetSchema
from . import listings, snapshots


def search(**kwargs):
    # To-do: handle filtering
    with db.session_scope() as session:
        beatmapsets = db.get_beatmapsets(session=session)
        beatmapsets_data = BeatmapsetSchema(many=True).dump(beatmapsets)

    return beatmapsets_data, 200


def post(body: dict):
    beatmapset_id = body["beatmapset_id"]

    try:
        bm = BeatmapManager()
        beatmap_ids = bm.archive(beatmapset_id)

        if any(beatmap_ids):
            response = []

            for beatmap_id in beatmap_ids:
                snapshot_number = db.get_beatmap_snapshot(beatmap_id=beatmap_id, _reversed=True).snapshot_number

                response.append({
                    "beatmap_id": beatmap_id,
                    "snapshot_number": snapshot_number
                })

            return response, 201
        else:
            return {"message": "The latest versions of all the beatmaps in the beatmapset have already been downloaded, no further action is needed"}, 200
    except httpx.HTTPStatusError as e:
        return e.response.json(), e.response.status_code
