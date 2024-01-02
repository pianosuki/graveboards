from app import cr
from app.schemas import leaderboards_schema, leaderboard_schema


def search():
    leaderboards = cr.get_leaderboards()
    return leaderboards_schema.dump(leaderboards), 200


def get(beatmap_id: int):
    leaderboard = cr.get_leaderboard(beatmap_id=beatmap_id)
    return leaderboard_schema.dump(leaderboard), 200


def post(body: dict):
    beatmap_id = body["beatmap_id"]
    latest_beatmap_version = cr.get_latest_beatmap_version(beatmap_id)
    version_number = body.get("version_number", latest_beatmap_version.version_number)
    cr.add_leaderboard(beatmap_id, latest_beatmap_version.id)
    print(f"Added leaderboard for beatmap {beatmap_id}/{version_number}")
