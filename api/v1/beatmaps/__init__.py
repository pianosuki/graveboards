from app import cr
from app.schemas import beatmaps_schema, beatmap_schema
from . import snapshots, difficulty


def search():
    beatmaps = cr.get_beatmaps()
    return beatmaps_schema.dump(beatmaps), 200


def get(beatmap_id: int):
    beatmap = cr.get_beatmap(id=beatmap_id)
    return beatmap_schema.dump(beatmap), 200
