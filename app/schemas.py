import json
from typing import Any

from marshmallow import fields, Schema, post_dump
from marshmallow.utils import EXCLUDE, RAISE

from app import db, ma
from .models import User, Score, Beatmap, Leaderboard, BeatmapSnapshot, Beatmapset, BeatmapsetSnapshot, ScoreFetcherTask, Request, BeatmapsetListing
from .utils import combine_checksums

__all__ = [
    "user_schema",
    "users_schema",
    "oauth_token_schema",
    "score_fetcher_task_schema",
    "beatmap_schema",
    "beatmaps_schema",
    "beatmap_snapshot_schema",
    "beatmap_snapshots_schema",
    "beatmapset_schema",
    "beatmapsets_schema",
    "beatmapset_snapshot_schema",
    "beatmapset_snapshots_schema",
    "beatmapset_listing_schema",
    "beatmapset_listings_schema",
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

    snapshots = fields.Method("dump_snapshots", "load_snapshots")

    def dump_snapshots(self, obj) -> dict[str, str]:
        return {value.snapshot_number: value.checksum for value in obj.snapshots}

    def load_snapshots(self, value) -> list[BeatmapSnapshot]:
        return [BeatmapSnapshot.query.filter_by(snapshot_number=key, checksum=value) for key, value in sorted(value.items())]


class BeatmapSnapshotSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = BeatmapSnapshot
        load_instance = True
        sqla_session = db.session
        unknown = EXCLUDE

    id = fields.Integer(dump_only=True)
    beatmap_id = fields.Integer()

    def load(self, data, *args):
        if not self.many:
            data["beatmap_id"] = data["id"]
            data["snapshot_number"] = len(Beatmap.query.get(data["beatmap_id"]).snapshots) + 1

        return super().load(data, *args)


class BeatmapsetSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Beatmapset
        load_instance = True
        sqla_session = db.session
        unknown = EXCLUDE
        include_relationships = True

    snapshots = fields.Method("dump_snapshots", "load_snapshots")

    def dump_snapshots(self, obj) -> dict[str, str]:
        return {value.snapshot_number: value.checksum for value in obj.snapshots}

    def load_snapshots(self, value) -> list[BeatmapsetSnapshot]:
        return [BeatmapsetSnapshot.query.filter_by(snapshot_number=key, checksum=value) for key, value in sorted(value.items())]


class BeatmapsetSnapshotSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = BeatmapsetSnapshot
        load_instance = True
        sqla_session = db.session
        unknown = EXCLUDE

    id = fields.Integer(dump_only=True)
    beatmapset_id = fields.Integer()
    covers = fields.Nested("CoversSchema")
    hype = fields.Nested("HypeSchema", allow_none=True)
    beatmap_snapshots = fields.Nested("BeatmapSnapshotSchema", many=True, dump_only=True)

    def load(self, data, *args):
        if not self.many:
            data["beatmapset_id"] = data["id"]
            data["snapshot_number"] = len(Beatmapset.query.get(data["beatmapset_id"]).snapshots) + 1
            data["checksum"] = combine_checksums([beatmap["checksum"] for beatmap in data["beatmaps"]])
            data["beatmap_snapshots"] = data["beatmaps"]

        return super().load(data, *args)


class BeatmapsetListingSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = BeatmapsetListing
        load_instance = True
        sqla_session = db.session
        include_relationships = True

    beatmapset_snapshot = fields.Nested("BeatmapsetSnapshotSchema")

    @post_dump
    def add_display_data(self, data, many: bool, **kwargs):
        from app import oac

        beatmapset_snapshot = data["beatmapset_snapshot"]
        display_data = {
            "title": beatmapset_snapshot["title"],
            "artist": beatmapset_snapshot["artist"],
            "thumbnail": beatmapset_snapshot["covers"]["list@2x"],
            "mapper": beatmapset_snapshot["creator"],
            "mapper_avatar": oac.get_user(beatmapset_snapshot["user_id"])["avatar_url"],
            "length": max(beatmapset_snapshot["beatmap_snapshots"], key=lambda beatmap_snapshot: beatmap_snapshot["total_length"])["total_length"],
            "difficulties": [beatmap_snapshot["difficulty_rating"] for beatmap_snapshot in beatmapset_snapshot["beatmap_snapshots"]],
        }

        data["display_data"] = BeatmapsetListingDisplayDataSchema().dump(display_data)
        return data


class BeatmapsetListingDisplayDataSchema(Schema):
    title = fields.String()
    artist = fields.String()
    thumbnail = fields.String()
    mapper = fields.String()
    mapper_avatar = fields.String()
    length = fields.Integer()
    difficulties = fields.List(fields.Float())
    verified = fields.Boolean()


class LeaderboardSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Leaderboard
        load_instance = True
        sqla_session = db.session
        include_relationships = True
        exclude = ("beatmap",)

    id = fields.Integer(load_only=True)
    beatmap_id = fields.Integer()
    snapshot_number = fields.Integer(dump_only=True)

    def dump(self, obj, *args):
        if self.many is False:
            obj.snapshot_number = BeatmapSnapshot.query.get(obj.beatmap_snapshot_id).snapshot_number
        elif self.many is True:
            for leaderboard in obj:
                leaderboard.snapshot_number = BeatmapSnapshot.query.get(leaderboard.beatmap_snapshot_id).snapshot_number

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
        if not self.many:
            beatmap_data = data["beatmap"]
            user = User.query.get(data["user_id"])
            beatmap = Beatmap.query.get(beatmap_data["id"])
            beatmapset = Beatmapset.query.get(beatmap_data["beatmapset_id"])
            beatmap_snapshot = BeatmapSnapshot.query.filter_by(checksum=beatmap_data["checksum"]).one()
            leaderboard = Leaderboard.query.filter_by(beatmap_snapshot_id=beatmap_snapshot.id).one()
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

    user_id = fields.Integer()
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
beatmap_snapshot_schema = BeatmapSnapshotSchema()
beatmap_snapshots_schema = BeatmapSnapshotSchema(many=True)
beatmapset_schema = BeatmapsetSchema()
beatmapsets_schema = BeatmapsetSchema(many=True)
beatmapset_snapshot_schema = BeatmapsetSnapshotSchema()
beatmapset_snapshots_schema = BeatmapsetSnapshotSchema(many=True)
beatmapset_listing_schema = BeatmapsetListingSchema()
beatmapset_listings_schema = BeatmapsetListingSchema(many=True)
leaderboard_schema = LeaderboardSchema()
leaderboards_schema = LeaderboardSchema(many=True)
score_schema = ScoreSchema()
scores_schema = ScoreSchema(many=True)
request_schema = RequestSchema()
requests_schema = RequestSchema(many=True)
