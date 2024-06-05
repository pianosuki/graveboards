from flask import send_file

from app import bm, cr


def search(beatmap_id: int):
    beatmap_versions = cr.get_beatmap_versions(beatmap_id=beatmap_id)
    return {beatmap_version.version_number: beatmap_version.checksum for beatmap_version in beatmap_versions}


def get(beatmap_id: int, version_number: int):
    beatmap_path = bm.get_path(beatmap_id, version_number)
    return send_file(beatmap_path), 200
