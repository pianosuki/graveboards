from app import cr
from app.schemas import leaderboard_schema


def search(beatmap_id: int):
    leaderboards = cr.get_leaderboards(beatmap_id=beatmap_id)
    beatmap_versions = cr.get_beatmap_versions(beatmap_id=beatmap_id)
    filtered_beatmap_versions = [beatmap_version for beatmap_version in beatmap_versions if beatmap_version.id in [leaderboard.beatmap_version_id for leaderboard in leaderboards]]
    return {beatmap_version.version_number: beatmap_version.checksum for beatmap_version in filtered_beatmap_versions}, 200


def get(beatmap_id: int, version_number: int):
    beatmap_version = cr.get_beatmap_version(beatmap_id=beatmap_id, version_number=version_number)
    leaderboard = cr.get_leaderboard(beatmap_id=beatmap_id, beatmap_version_id=beatmap_version.id)
    return leaderboard_schema.dump(leaderboard), 200
