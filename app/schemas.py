import json
from typing import Any

from marshmallow import fields, Schema
from marshmallow.utils import EXCLUDE, RAISE

from app import db, ma
from .models import User, Score, Beatmap, Leaderboard, BeatmapVersion, Beatmapset, ScoreFetcherTask, Request

__all__ = [
    "user_schema",
    "users_schema",
    "oauth_token_schema",
    "score_fetcher_task_schema",
    "beatmap_schema",
    "beatmaps_schema",
    "beatmap_version_schema",
    "beatmap_versions_schema",
    "beatmapset_schema",
    "beatmapsets_schema",
    "leaderboard_schema",
    "leaderboards_schema",
    "score_schema",
    "scores_schema",
    "request_schema",
    "requests_schema"
]


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        sqla_session = db.session
        include_relationships = True


class OauthTokenSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        sqla_session = db.session
        unknown = EXCLUDE


class ScoreFetcherTaskSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ScoreFetcherTask
        load_instance = True
        sqla_session = db.session


class BeatmapSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Beatmap
        load_instance = True
        sqla_session = db.session
        include_relationships = True

    versions = fields.Method("dump_versions", "load_versions")

    def dump_versions(self, obj) -> dict[str, str]:
        return {value.version_number: value.checksum for value in obj.versions}

    def load_versions(self, value) -> list[BeatmapVersion]:
        return [BeatmapVersion.query.filter_by(number=key, checksum=value) for key, value in sorted(value.items())]


class BeatmapVersionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = BeatmapVersion
        load_instance = True
        sqla_session = db.session
        unknown = EXCLUDE

    id = fields.Integer(dump_only=True)
    beatmap_id = fields.Integer()

    def load(self, data, *args):
        if self.many is False:
            data["beatmap_id"] = data["id"]
            data["version_number"] = len(Beatmap.query.get(data["beatmap_id"]).versions) + 1
        return super().load(data, *args)


class BeatmapsetSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Beatmapset
        load_instance = True
        sqla_session = db.session
        unknown = EXCLUDE

    covers = fields.Nested("CoversSchema")
    hype = fields.Nested("HypeSchema", allow_none=True)


class LeaderboardSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Leaderboard
        load_instance = True
        sqla_session = db.session
        include_relationships = True
        exclude = ("beatmap",)

    id = fields.Integer(load_only=True)
    beatmap_id = fields.Integer()
    version_number = fields.Integer(dump_only=True)

    def dump(self, obj, *args):
        if self.many is False:
            obj.version_number = BeatmapVersion.query.get(obj.beatmap_version_id).version_number
        elif self.many is True:
            for leaderboard in obj:
                leaderboard.version_number = BeatmapVersion.query.get(leaderboard.beatmap_version_id).version_number
        return super().dump(obj, *args)


class ScoreSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Score
        load_instance = True
        sqla_session = db.session
        unknown = EXCLUDE
        exclude = ("id",)

    user_id = fields.Integer(load_only=True)
    beatmap_id = fields.Integer(load_only=True)
    beatmapset_id = fields.Integer(load_only=True)
    leaderboard_id = fields.Integer(load_only=True)
    mods = fields.Method("dump_mods", "load_mods")
    statistics = fields.Nested("StatisticsSchema")

    def load(self, data, *args):
        if self.many is False:
            beatmap_data = data["beatmap"]
            user = User.query.get(data["user_id"])
            beatmap = Beatmap.query.get(beatmap_data["id"])
            beatmapset = Beatmapset.query.get(beatmap_data["beatmapset_id"])
            beatmap_version = BeatmapVersion.query.filter_by(checksum=beatmap_data["checksum"]).one()
            leaderboard = Leaderboard.query.filter_by(beatmap_version_id=beatmap_version.id).one()
            data["user_id"] = user.id
            data["beatmap_id"] = beatmap.id
            data["beatmapset_id"] = beatmapset.id
            data["leaderboard_id"] = leaderboard.id
        return super().load(data, *args)

    def dump_mods(self, obj) -> list:
        return json.loads(obj.mods) if obj.mods else []

    def load_mods(self, value) -> str:
        return json.dumps(value) if value else "[]"


class RequestSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Request
        load_instance = True
        sqla_session = db.session

    beatmapset_id = fields.Integer()


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


class HypeSchema(JSONTextSchema):
    current = fields.Integer()
    required = fields.Integer()


class StatisticsSchema(JSONTextSchema):
    count_100 = fields.Integer()
    count_300 = fields.Integer()
    count_50 = fields.Integer()
    count_geki = fields.Integer()
    count_katu = fields.Integer()
    count_miss = fields.Integer()


user_schema = UserSchema()
users_schema = UserSchema(many=True)
oauth_token_schema = OauthTokenSchema()
score_fetcher_task_schema = ScoreFetcherTaskSchema()
beatmap_schema = BeatmapSchema()
beatmaps_schema = BeatmapSchema(many=True)
beatmap_version_schema = BeatmapVersionSchema()
beatmap_versions_schema = BeatmapVersionSchema(many=True)
beatmapset_schema = BeatmapsetSchema()
beatmapsets_schema = BeatmapsetSchema(many=True)
leaderboard_schema = LeaderboardSchema()
leaderboards_schema = LeaderboardSchema(many=True)
score_schema = ScoreSchema()
scores_schema = ScoreSchema(many=True)
request_schema = RequestSchema()
requests_schema = RequestSchema(many=True)
