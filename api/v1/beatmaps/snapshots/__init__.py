from api.utils import prime_query_kwargs
from app import db
from app.database.schemas import BeatmapSnapshotSchema
from . import osu


def search(beatmap_id: int, **kwargs):
    prime_query_kwargs(kwargs)

    with db.session_scope() as session:
        beatmap_snapshots = db.get_beatmap_snapshots(beatmap_id=beatmap_id, session=session, **kwargs)
        beatmap_snapshots_data = BeatmapSnapshotSchema(many=True).dump(beatmap_snapshots)

    return beatmap_snapshots_data, 200


def get(beatmap_id: int, snapshot_number: int):
    with db.session_scope() as session:
        beatmap_snapshot = db.get_beatmap_snapshot(beatmap_id=beatmap_id, snapshot_number=snapshot_number, session=session)
        beatmap_snapshot_data = BeatmapSnapshotSchema().dump(beatmap_snapshot)

    return beatmap_snapshot_data, 200
