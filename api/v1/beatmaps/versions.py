from flask import send_file
from app import bm
from app.models import BeatmapVersion, Beatmap


def search(beatmap_id: int):
    beatmap = Beatmap.query.filter_by(beatmap_id=beatmap_id).one()
    beatmap_versions = BeatmapVersion.query.filter_by(beatmap_id=beatmap.id).all()
    return [item.id for item in beatmap_versions]


def get(beatmap_id: int, version_id: int):
    beatmap_path = bm.get_path(beatmap_id, version_id)
    return send_file(beatmap_path), 200
