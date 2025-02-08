from connexion import request

from api.utils import prime_query_kwargs
from app.database import PostgresqlDB
from app.database.schemas import BeatmapSnapshotSchema
from . import osu


async def search(beatmap_id: int, **kwargs):
    db: PostgresqlDB = request.state.db

    prime_query_kwargs(kwargs)

    beatmap_snapshots = await db.get_beatmap_snapshots(
        beatmap_id=beatmap_id,
        _exclude_lazy=True,
        **kwargs
    )
    beatmap_snapshots_data = [
        BeatmapSnapshotSchema.model_validate(beatmap_snapshot).model_dump(
            exclude={"leaderboard", "beatmapset_snapshots"}
        )
        for beatmap_snapshot in beatmap_snapshots
    ]

    return beatmap_snapshots_data, 200


async def get(beatmap_id: int, snapshot_number: int):
    db: PostgresqlDB = request.state.db

    beatmap_snapshot = await db.get_beatmap_snapshot(
        beatmap_id=beatmap_id,
        snapshot_number=snapshot_number,
        _exclude_lazy=True
    )

    if not beatmap_snapshot:
        return {"message": f"BeatmapSnapshot with beatmap_id '{beatmap_id}' and snapshot_number '{snapshot_number}' not found"}, 404

    beatmap_snapshot_data = BeatmapSnapshotSchema.model_validate(beatmap_snapshot).model_dump(
        exclude={"leaderboard", "beatmapset_snapshots"}
    )

    return beatmap_snapshot_data, 200
