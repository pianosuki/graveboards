from connexion import request

from api.utils import prime_query_kwargs
from app.database import PostgresqlDB
from app.database.schemas import LeaderboardSchema


async def search(beatmap_id: int, **kwargs):
    db: PostgresqlDB = request.state.db

    prime_query_kwargs(kwargs)

    leaderboards = await db.get_leaderboards(
        beatmap_id=beatmap_id,
        _exclude_lazy=True,
        **kwargs
    )
    leaderboards_data = [
        LeaderboardSchema.model_validate(leaderboard).model_dump(
            exclude={"scores"}
        )
        for leaderboard in leaderboards
    ]

    return leaderboards_data, 200


async def get(beatmap_id: int, snapshot_number: int):
    db: PostgresqlDB = request.state.db

    beatmap_snapshot = await db.get_beatmap_snapshot(
        beatmap_id=beatmap_id,
        snapshot_number=snapshot_number,
    )

    if not beatmap_snapshot:
        return {"message": f"BeatmapSnapshot with beatmap_id '{beatmap_id}' and snapshot_number '{snapshot_number}' not found"}, 404

    leaderboard = await db.get_leaderboard(
        beatmap_id=beatmap_id,
        beatmap_snapshot_id=beatmap_snapshot.id,
        _exclude_lazy=True
    )

    if not leaderboard:
        return {"message": f"No Leaderboard found for beatmap_id '{beatmap_id}' and snapshot_number '{snapshot_number}'"}, 404

    leaderboard_data = LeaderboardSchema.model_validate(leaderboard).model_dump(
        exclude={"scores"}
    )

    return leaderboard_data, 200
