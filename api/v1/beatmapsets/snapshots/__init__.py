from app import cr
from app.schemas import beatmapset_snapshot_schema, beatmapset_snapshots_schema
from . import zip


def search(beatmapset_id: int):
    beatmapset_snapshots = cr.get_beatmapset_snapshots(beatmapset_id=beatmapset_id)
    return beatmapset_snapshots_schema.dump(beatmapset_snapshots), 200


def get(beatmapset_id: int, snapshot_number: int):
    beatmapset_snapshot = cr.get_beatmapset_snapshot(beatmapset_id=beatmapset_id, snapshot_number=snapshot_number)
    return beatmapset_snapshot_schema.dump(beatmapset_snapshot), 200
