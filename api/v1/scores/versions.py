from flask import abort

from app import cr
from app.utils import parse_iso8601


def post(beatmap_id: int, version_number: int, body: dict):
    user_id = body["user_id"]
    created_at = parse_iso8601(body["created_at"])

    if not cr.user_exists(user_id):
        abort(404, f"There is no authenticated user with ID '{user_id}'")

    if not cr.beatmap_exists(beatmap_id):
        abort(404, f"There is no beatmap with ID '{beatmap_id}'")

    beatmap_version = cr.get_beatmap_version(beatmap_id=beatmap_id, version_number=version_number)

    if not beatmap_version:
        abort(404, f"The beatmap with ID '{beatmap_id}' has no version number '{version_number}'")

    leaderboard = cr.get_leaderboard(beatmap_id=beatmap_id, beatmap_version_id=beatmap_version.id)

    if not leaderboard:
        abort(404, f"There is no leaderboard for the beatmap with ID '{beatmap_id}' and version ID '{beatmap_version.id}'")

    if not cr.score_unique(beatmap_id, created_at):
        abort(409, f"The score created at '{created_at}' on the beatmap with ID '{beatmap_id}' already exists")

    cr.add_score(body)
