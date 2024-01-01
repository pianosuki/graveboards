from flask import send_file
from app import bm
from app.models import BeatmapVersion, Beatmap


def search(beatmap_id: int):
    beatmap_versions = BeatmapVersion.query.filter_by(beatmap_id=beatmap_id).all()
    return {beatmap_version.number: beatmap_version.checksum for beatmap_version in beatmap_versions}


def get(beatmap_id: int, version_number: int):
    beatmap_path = bm.get_path(beatmap_id, version_number)
    return send_file(beatmap_path), 200
