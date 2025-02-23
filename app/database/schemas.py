from datetime import datetime
from typing import Optional, Any
from copy import copy

from pydantic.main import BaseModel
from pydantic.config import ConfigDict
from pydantic.fields import Field
from pydantic.functional_validators import model_validator
from pydantic.functional_serializers import field_serializer, model_serializer
from pydantic_core.core_schema import SerializationInfo, SerializerFunctionWrapHandler

from app.utils import combine_checksums
from .models import *

__all__ = [
    "UserSchema",
    "RoleSchema",
    "ProfileSchema",
    "ApiKeySchema",
    "OAuthTokenSchema",
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
    "TagSchema"
]


class BaseModelExtra:
    @model_serializer(mode="wrap")
    def serialize(self, nxt: SerializerFunctionWrapHandler, info: SerializationInfo) -> dict[str, Any]:
        serialized = nxt(self)

        if info.context and (exclusions := info.context.get("exclusions")):
            exclude = exclusions.get(self.__class__)

            if exclude:
                for field in exclude:
                    serialized.pop(field)

        return serialized


class UserSchema(BaseModel, BaseModelExtra):
    model_config = ConfigDict(from_attributes=True)

    id: int

    profile: Optional["ProfileSchema"] = None
    roles: list["RoleSchema"] = []
    scores: list["ScoreSchema"] = []
    tokens: list["OAuthTokenSchema"] = []
    queues: list["QueueSchema"] = []
    requests: list["RequestSchema"] = []
    beatmaps: list["BeatmapSchema"] = []
    beatmapsets: list["BeatmapsetSchema"] = []


class RoleSchema(BaseModel, BaseModelExtra):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class ProfileSchema(BaseModel, BaseModelExtra):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    user_id: int
    updated_at: Optional[datetime] = None
    avatar_url: Optional[str]
    username: Optional[str]
    country_code: Optional[str]
    graveyard_beatmapset_count: Optional[int]
    loved_beatmapset_count: Optional[int]
    pending_beatmapset_count: Optional[int]
    ranked_beatmapset_count: Optional[int]
    kudosu: Optional["KudosuSchema"] = None
    is_restricted: Optional[bool] = None

    @model_validator(mode="before")
    @classmethod
    def from_osu_api_format(cls, data: Any) -> Any:
        if isinstance(data, dict):
            data_copy = copy(data)
            data_copy["user_id"] = data_copy.pop("id")

            return data_copy

        return data


class ApiKeySchema(BaseModel, BaseModelExtra):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    user_id: int
    key: str
    created_at: Optional[datetime] = None
    expires_at: datetime
    is_revoked: bool = False


class OAuthTokenSchema(BaseModel, BaseModelExtra):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    user_id: int
    access_token: str
    expires_at: int
    is_revoked: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class JWTSchema(BaseModel, BaseModelExtra):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    user_id: int
    token: str
    issued_at: int
    expires_at: int
    is_revoked: bool = False
    updated_at: Optional[datetime] = None


class ScoreFetcherTaskSchema(BaseModel, BaseModelExtra):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    user_id: int
    enabled: bool = False
    last_fetch: Optional[datetime] = None


class ProfileFetcherTaskSchema(BaseModel, BaseModelExtra):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    user_id: int
    enabled: bool = True
    last_fetch: Optional[datetime] = None


class BeatmapSchema(BaseModel, BaseModelExtra):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    beatmapset_id: int
    user_id: int

    leaderboards: list["LeaderboardSchema"] = []
    snapshots: list["BeatmapSnapshotSchema"] = []


class BeatmapSnapshotSchema(BaseModel, BaseModelExtra):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    beatmap_id: int
    snapshot_number: Optional[int] = None
    snapshot_date: Optional[datetime] = None
    accuracy: float
    ar: float
    bpm: float
    checksum: str
    count_circles: int
    count_sliders: int
    count_spinners: int
    cs: float
    difficulty_rating: float
    drain: float
    failtimes: "FailtimesSchema"
    hit_length: int
    last_updated: datetime
    max_combo: int
    mode: str
    mode_int: int
    status: str
    total_length: int
    user_id: int
    version: str
    deleted_at: Optional[datetime]
    passcount: int
    playcount: int
    ranked: int
    url: str

    beatmapset_snapshots: list["BeatmapsetSnapshotSchema"] = []
    leaderboard: Optional["LeaderboardSchema"] = None
    owner_profiles: list["ProfileSchema"] = []

    @model_validator(mode="before")
    @classmethod
    def from_osu_api_format(cls, data: Any) -> Any:
        if isinstance(data, dict):
            data_copy = copy(data)
            data_copy["beatmap_id"] = data_copy.pop("id") if "beatmap_id" not in data_copy else data_copy["beatmap_id"]

            return data_copy

        return data


class BeatmapsetSchema(BaseModel, BaseModelExtra):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    user_id: int

    snapshots: list["BeatmapsetSnapshotSchema"] = []


class BeatmapsetSnapshotSchema(BaseModel, BaseModelExtra):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    beatmapset_id: int
    snapshot_number: Optional[int] = None
    snapshot_date: Optional[datetime] = None
    checksum: str
    verified: Optional[bool] = None
    artist: str
    artist_unicode: str
    availability: "AvailabilitySchema"
    covers: "CoversSchema"
    creator: str
    deleted_at: Optional[datetime]
    favourite_count: int
    genre: Optional[dict[str, int | str]]
    hype: Optional[dict[str, int]]
    language: Optional[dict[str, int | str]]
    last_updated: datetime
    nsfw: bool
    offset: int
    play_count: int
    preview_url: str
    ranked: int
    source: str
    status: str
    submitted_date: datetime
    title: str
    title_unicode: str
    track_id: Optional[int]
    user_id: int
    video: bool

    beatmap_snapshots: list["BeatmapSnapshotSchema"] = []
    tags: list["TagSchema"] = []
    user_profile: Optional["ProfileSchema"] = None

    def model_dump(self, **kwargs) -> dict:
        kwargs.setdefault("by_alias", True)
        return super().model_dump(**kwargs)

    @model_validator(mode="before")
    @classmethod
    def from_osu_api_format(cls, data: Any) -> Any:
        if isinstance(data, dict):
            data_copy = copy(data)
            data_copy["beatmapset_id"] = data_copy.pop("id")
            data_copy["checksum"] = combine_checksums([beatmap["checksum"] for beatmap in data_copy["beatmaps"]])
            data_copy["beatmap_snapshots"] = data_copy.pop("beatmaps")
            data_copy["tags"] = [{"name": tag.strip()} for tag in data_copy["tags"].strip().split(" ")]

            return data_copy

        return data

    @field_serializer("tags")
    def serialize_tags(self, tags: list["TagSchema"], _info: SerializationInfo) -> list[str]:
        return [tag.name for tag in tags]


class BeatmapsetListingSchema(BaseModel, BaseModelExtra):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    beatmapset_id: int
    beatmapset_snapshot_id: int
    updated_at: datetime

    beatmapset_snapshot: BeatmapsetSnapshotSchema

    def model_dump(self, **kwargs) -> dict:
        kwargs.setdefault("by_alias", True)
        return super().model_dump(**kwargs)


class LeaderboardSchema(BaseModel, BaseModelExtra):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    beatmap_id: int
    beatmap_snapshot_id: int

    scores: list["ScoreSchema"] = []


class ScoreSchema(BaseModel, BaseModelExtra):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    user_id: int
    beatmap_id: int
    beatmapset_id: int
    leaderboard_id: int
    accuracy: float
    created_at: datetime
    max_combo: int
    mode: str
    mode_int: int
    mods: list[str]
    perfect: bool
    pp: Optional[float] = None
    rank: str
    score: int
    statistics: "StatisticsSchema"
    type: str

    @model_validator(mode="before")
    @classmethod
    def from_osu_api_format(cls, data: Any) -> Any:
        if isinstance(data, dict):
            data_copy = copy(data)
            data_copy.pop("id", None)
            data_copy["beatmap_id"] = data_copy["beatmap"]["id"]
            data_copy["beatmapset_id"] = data_copy["beatmapset"]["id"]

            return data_copy

        return data


class QueueSchema(BaseModel, BaseModelExtra):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    user_id: int
    name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_open: Optional[bool] = None
    visibility: Optional[int] = None

    requests: list["RequestSchema"] = []
    managers: list["UserSchema"] = []
    user_profile: Optional["ProfileSchema"] = None
    manager_profiles: list["ProfileSchema"] = []


class RequestSchema(BaseModel, BaseModelExtra):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    user_id: int
    beatmapset_id: int
    queue_id: int
    comment: Optional[str] = None
    mv_checked: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    status: Optional[int] = None

    user_profile: Optional["ProfileSchema"] = None
    queue: Optional["QueueSchema"] = None


class RequestListingSchema(RequestSchema):
    beatmapset_snapshot: "BeatmapsetSnapshotSchema"

    def model_dump(self, **kwargs) -> dict:
        kwargs.setdefault("by_alias", True)
        return super().model_dump(**kwargs)

    @model_validator(mode="before")
    @classmethod
    def from_tuple(cls, data: Any) -> Any:
        if isinstance(data, tuple) and len(data) == 2:
            beatmapset_snapshot, request = data

            if not isinstance(beatmapset_snapshot, BeatmapsetSnapshotSchema):
                beatmapset_snapshot = BeatmapsetSnapshotSchema.model_validate(beatmapset_snapshot)

            if not isinstance(request, RequestSchema):
                request = RequestSchema.model_validate(request)

            return {
                **request.model_dump(),
                "beatmapset_snapshot": beatmapset_snapshot,
            }

        return data


class TagSchema(BaseModel, BaseModelExtra):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    name: str


class KudosuSchema(BaseModel, BaseModelExtra):
    available: int
    total: int


class FailtimesSchema(BaseModel, BaseModelExtra):
    exit: Optional[list[int]] = None
    fail: Optional[list[int]] = None


class AvailabilitySchema(BaseModel, BaseModelExtra):
    download_disabled: bool
    more_information: Optional[str] = None


class CoversSchema(BaseModel, BaseModelExtra):
    cover: str
    cover2x: str = Field(alias="cover@2x")
    card: str
    card2x: str = Field(alias="card@2x")
    list: str
    list2x: str = Field(alias="list@2x")
    slimcover: str
    slimcover2x: str = Field(alias="slimcover@2x")

    def model_dump(self, **kwargs) -> dict:
        kwargs.setdefault("by_alias", True)
        return super().model_dump(**kwargs)


class HypeSchema(BaseModel, BaseModelExtra):
    current: int
    required: int


class StatisticsSchema(BaseModel, BaseModelExtra):
    count_100: Optional[int]
    count_300: Optional[int]
    count_50: Optional[int]
    count_geki: Optional[int]
    count_katu: Optional[int]
    count_miss: Optional[int]
