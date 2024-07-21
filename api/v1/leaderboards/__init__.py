from flask import abort

from app import cr
from app.schemas import leaderboards_schema, leaderboard_schema
from . import snapshots


def search():
    leaderboards = cr.get_leaderboards()
    return leaderboards_schema.dump(leaderboards), 200


def get(beatmap_id: int):
    leaderboard = cr.get_leaderboard(beatmap_id=beatmap_id)
    return leaderboard_schema.dump(leaderboard), 200


def post(body: dict):
    beatmap_id = body["beatmap_id"]

    if not cr.beatmap_exists(beatmap_id):
        abort(404, f"There is no beatmap with ID '{beatmap_id}'")

    latest_beatmap_version = cr.get_latest_beatmap_version(beatmap_id)
    version_number = body.get("version_number", latest_beatmap_version.version_number)
    beatmap_version = cr.get_beatmap_version(beatmap_id=beatmap_id, version_number=version_number)

    if not beatmap_version:
        abort(404, f"The beatmap with ID '{beatmap_id}' has no version number '{version_number}'")

    leaderboard = cr.get_leaderboard(beatmap_id=beatmap_id, beatmap_version_id=beatmap_version.id)

    if leaderboard:
        abort(409, f"The leaderboard for the beatmap with ID '{beatmap_id}' and version number '{version_number}' already exists")

    cr.add_leaderboard(beatmap_id, latest_beatmap_version.id)
