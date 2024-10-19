from api.utils import prime_query_kwargs
from app import db
from app.database.schemas import BeatmapsetSnapshotSchema
from . import zip


def search(beatmapset_id: int, **kwargs):
    prime_query_kwargs(kwargs)

    with db.session_scope() as session:
        beatmapset_snapshots = db.get_beatmapset_snapshots(beatmapset_id=beatmapset_id, session=session, **kwargs)
        beatmapset_snapshots_data = BeatmapsetSnapshotSchema(many=True).dump(beatmapset_snapshots)

    return beatmapset_snapshots_data, 200


def get(beatmapset_id: int, snapshot_number: int):
    with db.session_scope() as session:
        beatmapset_snapshot = db.get_beatmapset_snapshot(beatmapset_id=beatmapset_id, snapshot_number=snapshot_number, session=session)
        beatmapset_snapshot_data = BeatmapsetSnapshotSchema().dump(beatmapset_snapshot)

    return beatmapset_snapshot_data, 200
