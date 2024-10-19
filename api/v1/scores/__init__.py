from api.utils import prime_query_kwargs
from app import db
from app.database.schemas import ScoreSchema
from app.utils import parse_iso8601
from app.security import authorization_required
from app.enums import RoleName


def search(**kwargs):
    # TODO: handle filtering

    prime_query_kwargs(kwargs)

    with db.session_scope() as session:
        scores = db.get_scores(session=session, **kwargs)
        scores_data = ScoreSchema(many=True).dump(scores)

    return scores_data, 200


@authorization_required(RoleName.ADMIN)
def post(body: dict, **kwargs):
    user_id = body["user_id"]
    beatmap_id = body["beatmap"]["id"]
    created_at = parse_iso8601(body["created_at"])

    if not db.get_user(id=user_id):
        return {"message": f"There is no user with ID '{user_id}'"}, 404

    if not db.get_beatmap(id=beatmap_id):
        return {"message": f"There is no beatmap with ID '{beatmap_id}'"}, 404

    beatmap_snapshot = db.get_beatmap_snapshot(beatmap_id=beatmap_id, _reversed=True)

    if not beatmap_snapshot:
        return {"message": f"There is no beatmap snapshot with beatmap ID '{beatmap_id}'"}, 404

    leaderboard = db.get_leaderboard(beatmap_id=beatmap_id, beatmap_snapshot_id=beatmap_snapshot.id)

    if not leaderboard:
        return {"message": f"There is no leaderboard with beatmap ID '{beatmap_id}' and snapshot ID '{beatmap_snapshot.id}'"}, 404

    if db.get_score(beatmap_id=beatmap_id, created_at=created_at):
        return {"message": f"The score created at '{created_at}' on the beatmap with ID '{beatmap_id}' already exists"}, 409

    db.add_score(body)

    return {"message": "Score added successfully!"}, 201
