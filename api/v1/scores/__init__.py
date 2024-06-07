from flask import abort

from api import v1 as api
from app import cr
from app.schemas import scores_schema
from . import versions


def search(**kwargs):
    # To-do: handle filtering
    scores = cr.get_scores()
    return scores_schema.dump(scores), 200


def post(body: dict):
    beatmap_id = body["beatmap"]["id"]

    if not cr.beatmap_exists(beatmap_id):
        abort(404, f"There is no beatmap with ID '{beatmap_id}'")

    beatmap_version = cr.get_latest_beatmap_version(beatmap_id)

    api.scores.versions.post(beatmap_id, beatmap_version.version_number, body)
