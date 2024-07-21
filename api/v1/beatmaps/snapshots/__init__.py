from app import cr
from app.schemas import beatmap_snapshot_schema, beatmap_snapshots_schema
from . import osu


def search(beatmap_id: int):
    beatmap_snapshots = cr.get_beatmap_snapshots(beatmap_id=beatmap_id)
    return beatmap_snapshots_schema.dump(beatmap_snapshots), 200


def get(beatmap_id: int, snapshot_number: int):
    beatmap_snapshot = cr.get_beatmap_snapshot(beatmap_id=beatmap_id, snapshot_number=snapshot_number)
    return beatmap_snapshot_schema.dump(beatmap_snapshot), 200
