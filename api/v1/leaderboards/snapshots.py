from api.utils import prime_query_kwargs
from app import db
from app.database.schemas import LeaderboardSchema


def search(beatmap_id: int, **kwargs):
    prime_query_kwargs(kwargs)

    with db.session_scope() as session:
        leaderboards = db.get_leaderboards(beatmap_id=beatmap_id, session=session, **kwargs)
        leaderboards_data = LeaderboardSchema(many=True).dump(leaderboards)

    return leaderboards_data, 200


def get(beatmap_id: int, snapshot_number: int):
    with db.session_scope() as session:
        beatmap_snapshot = db.get_beatmap_snapshot(beatmap_id=beatmap_id, snapshot_number=snapshot_number, session=session)
        leaderboard = db.get_leaderboard(beatmap_id=beatmap_id, beatmap_snapshot_id=beatmap_snapshot.id, session=session)

        leaderboard_data = LeaderboardSchema().dump(leaderboard)

    return leaderboard_data, 200
