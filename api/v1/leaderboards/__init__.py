from api.utils import prime_query_kwargs
from app import db
from app.database.schemas import LeaderboardSchema
from app.security import authorization_required
from app.enums import RoleName
from . import snapshots


def search(**kwargs):
    prime_query_kwargs(kwargs)

    with db.session_scope() as session:
        leaderboards = db.get_leaderboards(session=session, **kwargs)
        leaderboards_data = LeaderboardSchema(many=True).dump(leaderboards)

    return leaderboards_data, 200


def get(beatmap_id: int):
    with db.session_scope() as session:
        leaderboard = db.get_leaderboard(beatmap_id=beatmap_id, session=session)
        leaderboard_data = LeaderboardSchema().dump(leaderboard)

    return leaderboard_data, 200


@authorization_required(RoleName.ADMIN)
def post(body: dict, **kwargs):
    beatmap_id = body["beatmap_id"]

    if not db.beatmap_exists(beatmap_id):
        return f"There is no beatmap with ID '{beatmap_id}'", 404

    beatmap_snapshot = db.get_beatmap_snapshot(beatmap_id=beatmap_id, _reversed=True)

    if db.get_leaderboard(beatmap_id=beatmap_id, beatmap_snapshot_id=beatmap_snapshot.id):
        return {"message": f"The leaderboard for the beatmap snapshot with ID '{beatmap_id}' and snapshot number '{beatmap_snapshot.snapshot_number}' already exists"}, 409

    db.add_leaderboard(beatmap_id=beatmap_id, beatmap_snapshot_id=beatmap_snapshot.id)

    return {"message": "Leaderboard added successfully!"}, 201
