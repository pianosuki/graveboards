from app import db
from app.database.schemas import BeatmapSchema


def search():
    with db.session_scope() as session:
        beatmaps = db.get_beatmaps(session=session)
        beatmaps_data = BeatmapSchema(many=True).dump(beatmaps)

    return beatmaps_data, 200


def get(beatmap_id: int):
    with db.session_scope() as session:
        beatmap = db.get_beatmap(id=beatmap_id, session=session)
        beatmap_data = BeatmapSchema().dump(beatmap)

    return beatmap_data, 200
