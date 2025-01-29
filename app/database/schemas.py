import json
from typing import Any

from marshmallow import fields
from marshmallow.schema import Schema
from marshmallow.decorators import pre_dump, post_dump, pre_load
from marshmallow.utils import EXCLUDE, RAISE
from marshmallow.exceptions import ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, SQLAlchemySchema
from marshmallow_sqlalchemy.fields import Nested
from sqlalchemy.sql import select
from sqlalchemy.engine.row import Row

from app.utils import combine_checksums
from .models import *
from .schema_fields import *

__all__ = [
    "UserSchema",
    "RoleSchema",
    "ProfileSchema",
    "OauthTokenSchema",
    "JWTSchema",
    "ScoreFetcherTaskSchema",
    "ProfileFetcherTaskSchema",
    "BeatmapSchema",
    "BeatmapSnapshotSchema",
    "BeatmapsetSchema",
    "BeatmapsetSnapshotSchema",
    "BeatmapsetListingSchema",
    "LeaderboardSchema",
    "ScoreSchema",
    "QueueSchema",
    "RequestSchema",
    "RequestListingSchema",
    "TagSchema",
    "JSONTextSchema"
]


class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        include_relationships = True

    profile = fields.Nested("ProfileSchema")
    roles = fields.Nested("RoleSchema", many=True)


class RoleSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Role
        load_instance = True

    @pre_load
    def handle_role_identifier(self, data, *args, **kwargs):
        if "id" in data:
            role = self.session.get(Role, data["id"])
            data["name"] = role.name
        elif "name" in data:
            role = self.session.scalar(select(Role).filter_by(name=data["name"]))
            data["id"] = role.id
        else:
            raise ValidationError("Invalid input format")

        return data


class ProfileSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Profile
        load_instance = True
        include_fk = True
        unknown = EXCLUDE

    kudosu = fields.Nested("KudosuSchema")

    @pre_load
    def pre_load(self, data, *args, **kwargs):
        if not self.many:
            data["user_id"] = data.pop("id")

        return data


class OauthTokenSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = OauthToken
        load_instance = True
        unknown = EXCLUDE


class JWTSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = JWT
        load_instance = True
        include_fk = True
        unknown = EXCLUDE
        exclude = ("id",)


class ScoreFetcherTaskSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ScoreFetcherTask
        load_instance = True

    last_fetch = CustomDateTime()


class ProfileFetcherTaskSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ProfileFetcherTask
        load_instance = True

    last_fetch = CustomDateTime()


class BeatmapSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Beatmap
        load_instance = True
        include_relationships = True

    snapshots = fields.Method("dump_snapshots", "load_snapshots")

    def dump_snapshots(self, obj) -> dict[str, str]:
        return {value.snapshot_number: value.checksum for value in obj.snapshots}

    def load_snapshots(self, value) -> list[BeatmapSnapshot]:
        return [self.session.scalar(select(BeatmapSnapshot).filter_by(snapshot_number=key, checksum=value)) for key, value in sorted(value.items())]


class BeatmapSnapshotSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = BeatmapSnapshot
        load_instance = True
        include_fk = True
        unknown = EXCLUDE

    id = fields.Integer(dump_only=True)

    @pre_load
    def pre_load(self, data, *args, **kwargs):
        if not self.many:
            beatmap_id = data["id"]
            snapshot_count = self.session.scalar(select(Beatmap.num_snapshots).where(Beatmap.id == beatmap_id))

            data["beatmap_id"] = beatmap_id
            data["snapshot_number"] = snapshot_count + 1

        return data


class BeatmapsetSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Beatmapset
        load_instance = True
        include_relationships = True
        unknown = EXCLUDE

    snapshots = fields.Method("dump_snapshots", "load_snapshots")

    def dump_snapshots(self, obj) -> dict[str, str]:
        return {value.snapshot_number: value.checksum for value in obj.snapshots}

    def load_snapshots(self, value) -> list[BeatmapsetSnapshot]:
        return [self.session.scalar(select(BeatmapsetSnapshot).filter_by(snapshot_number=key, checksum=value)) for key, value in sorted(value.items())]


class BeatmapsetSnapshotSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = BeatmapsetSnapshot
        load_instance = True
        include_fk = True
        include_relationships = True
        unknown = EXCLUDE

    id = fields.Integer(dump_only=True)
    covers = fields.Nested("CoversSchema")
    hype = fields.Nested("HypeSchema", allow_none=True)
    beatmap_snapshots = Nested("BeatmapSnapshotSchema", many=True, dump_only=True)
    tags = Nested("TagSchema", many=True, dump_only=True)
    user_profile = fields.Nested("ProfileSchema", dump_only=True)

    @pre_load
    def pre_load(self, data, *args, **kwargs):
        if not self.many:
            data["beatmapset_id"] = data["id"]
            data["snapshot_number"] = self.session.scalar(select(Beatmapset.num_snapshots).where(Beatmapset.id == data["id"])) + 1
            data["checksum"] = combine_checksums([beatmap["checksum"] for beatmap in data["beatmaps"]])
            data["beatmap_snapshots"] = data["beatmaps"]

        return data


class BeatmapsetListingSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = BeatmapsetListing
        load_instance = True
        include_relationships = True

    beatmapset_snapshot = fields.Nested("BeatmapsetSnapshotSchema")


class LeaderboardSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Leaderboard
        load_instance = True
        include_relationships = True
        include_fk = True

    id = fields.Integer(load_only=True)
    snapshot_number = fields.Integer(dump_only=True)

    @pre_dump
    def pre_dump(self, data, *args, **kwargs):
        if self.many is False:
            data.snapshot_number = self.session.get(BeatmapSnapshot, data.beatmap_snapshot_id).snapshot_number
        elif self.many is True:
            for leaderboard in data:
                leaderboard.snapshot_number = self.session.get(BeatmapSnapshot, leaderboard.beatmap_snapshot_id).snapshot_number

        return data


class ScoreSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Score
        load_instance = True
        include_fk = True
        unknown = EXCLUDE
        exclude = ("id",)

    user_id = fields.Integer(load_only=True)
    beatmap_id = fields.Integer(load_only=True)
    beatmapset_id = fields.Integer(load_only=True)
    leaderboard_id = fields.Integer(load_only=True)
    mods = fields.Method("dump_mods", "load_mods")
    statistics = fields.Nested("StatisticsSchema")

    @pre_load
    def pre_load(self, data, *args, **kwargs):
        if not self.many:
            beatmap_data = data["beatmap"]

            user = self.session.get(User, data["user_id"])
            beatmap = self.session.get(Beatmap, beatmap_data["id"])
            beatmapset = self.session.get(Beatmapset, beatmap_data["beatmapset_id"])
            beatmap_snapshot = self.session.scalar(select(BeatmapSnapshot).filter_by(checksum=beatmap_data["checksum"]))
            leaderboard = self.session.scalar(select(Leaderboard).filter_by(beatmap_snapshot_id=beatmap_snapshot.id))

            data["user_id"] = user.id
            data["beatmap_id"] = beatmap.id
            data["beatmapset_id"] = beatmapset.id
            data["leaderboard_id"] = leaderboard.id

        return data

    def dump_mods(self, obj) -> list:
        return json.loads(obj.mods) if obj.mods else []

    def load_mods(self, value) -> str:
        return json.dumps(value) if value else "[]"


class QueueSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Queue
        load_instance = True
        include_fk = True

    user_profile = fields.Nested("ProfileSchema", dump_only=True)
    manager_profiles = fields.Nested("ProfileSchema", many=True, dump_only=True)


class RequestSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Request
        load_instance = True
        include_fk = True

    user_profile = fields.Nested("ProfileSchema", dump_only=True)
    queue = fields.Nested("QueueSchema", dump_only=True)


class RequestListingSchema(SQLAlchemySchema):
    def _serialize(self, obj: Any, many: bool | None = None) -> dict | list[dict]:
        def get_serialized_dict(beatmapset_listing_: BeatmapsetListing, request_: Request) -> dict:
            return {
                **RequestSchema().dump(request_),
                "beatmapset_snapshot": BeatmapsetSnapshotSchema(session=self.session).dump(beatmapset_listing_.beatmapset_snapshot),
            }

        if not (self.many or many):
            if not isinstance(obj, (tuple, Row)):
                raise TypeError("Data structure must be a tuple")

            beatmapset_listing, request = obj
            return get_serialized_dict(beatmapset_listing, request)
        else:
            if not isinstance(obj, list) or not all([isinstance(item, (tuple, Row)) for item in obj]):
                raise TypeError("Data structure must be a list of tuples")

            return [get_serialized_dict(beatmapset_listing, request) for beatmapset_listing, request in obj]


class TagSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Tag
        load_instance = True

    @post_dump
    def post_dump(self, data, *args, **kwargs):
        return data["name"]


class JSONTextSchema(Schema):
    def _serialize(self, obj: str, many: bool = False) -> Any | None:
        return json.loads(obj) if obj is not None else None

    def _deserialize(self, data, *, error_store, many: bool = False, partial=None, unknown=RAISE, index=None) -> str | None:
        return json.dumps(data) if data is not None else None


class KudosuSchema(JSONTextSchema):
    available = fields.Integer()
    total = fields.Integer()


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
