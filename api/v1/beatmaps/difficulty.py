from flask import abort

from app import cr, bm


def search(beatmap_id: int):
    if not cr.beatmap_exists(beatmap_id):
        abort(404, f"There is no beatmap with ID '{beatmap_id}'")

    beatmap_version = cr.get_latest_beatmap_version(beatmap_id)

    return get(beatmap_id, beatmap_version.id)


def get(beatmap_id: int, version_number: int):
    if not cr.beatmap_exists(beatmap_id):
        abort(404, f"There is no beatmap with ID '{beatmap_id}'")

    beatmap_version = cr.get_beatmap_version(beatmap_id=beatmap_id, version_number=version_number)

    if not beatmap_version:
        abort(404, f"The beatmap with ID '{beatmap_id}' has no version number '{version_number}'")

    beatmap_path = bm.get_path(beatmap_id, version_number)

    # Not implemented
