import json
from typing import Any
from marshmallow import fields, Schema
from marshmallow.utils import EXCLUDE, RAISE
from app import db, ma
from .models import User, Score, Beatmap, Leaderboard, BeatmapVersion, Beatmapset
from .utils import convert_instrumentedlist_to_dict

__all__ = [
    "user_schema",
    "users_schema",
    "beatmap_schema",
    "beatmaps_schema",
    "beatmap_version_schema",
    "beatmapset_schema",
    "score_schema"
]


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        sqla_session = db.session
        include_relationships = True


class BeatmapSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Beatmap
        load_instance = True
        sqla_session = db.session
        include_relationships = True

    versions = fields.Method("dump_versions", "load_versions")

    def dump_versions(self, obj) -> dict[str, str]:
        return {key: value.checksum for key, value in convert_instrumentedlist_to_dict(obj.versions).items()}

    def load_versions(self, value) -> list[BeatmapVersion]:
        return [BeatmapVersion.query.get(item) for item in sorted(value.keys())]


class BeatmapVersionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = BeatmapVersion
        load_instance = True
        sqla_session = db.session
        unknown = EXCLUDE

    id = fields.Integer(dump_only=True)
    beatmap_id = fields.Integer()

    def load(self, data, *args, many=None, partial=None, unknown=None):
        beatmap = Beatmap.query.filter_by(beatmap_id=data["id"]).one()
        data["beatmap_id"] = beatmap.id
        return super().load(data, *args, many=many, partial=partial, unknown=unknown)


class BeatmapsetSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Beatmapset
        load_instance = True
        sqla_session = db.session
        unknown = EXCLUDE

    id = fields.Integer(dump_only=True)
    covers = fields.Nested("CoversSchema")

    def load(self, data, *args, many=None, partial=None, unknown=None):
        data["beatmapset_id"] = data["id"]
        return super().load(data, *args, many=many, partial=partial, unknown=unknown)


class ScoreSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Score
        load_instance = True
        sqla_session = db.session
        unknown = EXCLUDE

    id = fields.Integer(dump_only=True)
    user_id = fields.Integer()
    beatmap_id = fields.Integer()
    leaderboard_id = fields.Integer()
    mods = fields.Method("dump_mods", "load_mods")
    statistics = fields.Nested("StatisticsSchema")

    def load(self, data, *args, many=None, partial=None, unknown=None):
        beatmap_data = data["beatmap"]
        user = User.query.filter_by(osu_id=data["user_id"])
        beatmap = Beatmap.query.filter_by(beatmap_id=beatmap_data["id"])
        beatmap_version = BeatmapVersion.query.filter_by(checksum=beatmap_data["checksum"])
        leaderboard = Leaderboard.query.filter_by(beatmap_version_id=beatmap_version.id)
        data["user_id"] = user.id
        data["beatmap_id"] = beatmap.id
        data["leaderboard_id"] = leaderboard.id
        return super().load(data, *args, many=many, partial=partial, unknown=unknown)

    def dump_mods(self, obj) -> list:
        return json.loads(obj.mods) if obj.mods else []

    def load_mods(self, value) -> str:
        return json.dumps(value) if value else "[]"


class JSONTextSchema(Schema):
    def _serialize(self, obj: str, many: bool = False) -> Any | None:
        return json.loads(obj) if obj is not None else None

    def _deserialize(self, data, *, error_store, many: bool = False, partial=None, unknown=RAISE, index=None) -> str | None:
        return json.dumps(data) if data is not None else None


class CoversSchema(JSONTextSchema):
    cover = fields.String()
    cover2x = fields.String(data_key="cover@2x")
    card = fields.String()
    card2x = fields.String(data_key="card@2x")
    list = fields.String()
    list2x = fields.String(data_key="list@2x")
    slimcover = fields.String()
    slimcover2x = fields.String(data_key="slimcover@2x")


class StatisticsSchema(JSONTextSchema):
    count_100 = fields.Integer()
    count_300 = fields.Integer()
    count_50 = fields.Integer()
    count_geki = fields.Integer()
    count_katu = fields.Integer()
    count_miss = fields.Integer()


user_schema = UserSchema()
users_schema = UserSchema(many=True)
beatmap_schema = BeatmapSchema()
beatmaps_schema = BeatmapSchema(many=True)
beatmap_version_schema = BeatmapVersionSchema()
beatmapset_schema = BeatmapsetSchema()
score_schema = ScoreSchema()
