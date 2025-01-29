import json
from datetime import datetime
from enum import Enum
from typing import Optional, TypeVar, Any

from sqlalchemy.sql import select
from sqlalchemy.sql.schema import Table, Column, ForeignKey, UniqueConstraint
from sqlalchemy.sql.sqltypes import Integer, String, DateTime, Text, Boolean, Float
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.expression import cast
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import relationship, mapped_column
from sqlalchemy.orm.decl_api import DeclarativeBase
from sqlalchemy.orm.base import Mapped
from sqlalchemy.orm.mapper import Mapper
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.dialects.postgresql.json import JSONB

from app.utils import aware_utcnow

__all__ = [
    "BaseType",
    "ModelClass",
    "Base",
    "User",
    "Role",
    "Profile",
    "ApiKey",
    "OauthToken",
    "JWT",
    "ScoreFetcherTask",
    "ProfileFetcherTask",
    "Beatmap",
    "BeatmapSnapshot",
    "Beatmapset",
    "BeatmapsetSnapshot",
    "BeatmapsetListing",
    "Leaderboard",
    "Score",
    "Queue",
    "Request",
    "Tag",
    "user_role_association",
    "beatmap_snapshot_beatmapset_snapshot_association",
    "queue_manager_association"
]


class Base(DeclarativeBase):
    def to_dict(self) -> dict[str, Any]:
        return {key: value for key, value in self.__dict__.items() if not key.startswith("_")}


BaseType = TypeVar("BaseType", bound=Base)

user_role_association = Table(
    "user_role_association", Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True)
)

beatmap_snapshot_beatmapset_snapshot_association = Table(
    "beatmap_snapshot_beatmapset_snapshot_association", Base.metadata,
    Column("beatmap_snapshot_id", Integer, ForeignKey("beatmap_snapshots.id"), primary_key=True),
    Column("beatmapset_snapshot_id", Integer, ForeignKey("beatmapset_snapshots.id"), primary_key=True)
)

queue_manager_association = Table(
    "queue_manager_association", Base.metadata,
    Column("queue_id", Integer, ForeignKey("queues.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True)
)

tag_beatmapset_snapshot_association = Table(
    "tag_beatmapset_snapshot_association", Base.metadata,
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
    Column("beatmapset_snapshot_id", Integer, ForeignKey("beatmapset_snapshots.id"), primary_key=True)
)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)

    # Relationships
    profile: Mapped["Profile"] = relationship("Profile", backref="user", uselist=False, lazy=True)
    roles: Mapped[list["Role"]] = relationship("Role", secondary=user_role_association, lazy=True)
    scores: Mapped[list["Score"]] = relationship("Score", lazy=True)
    tokens: Mapped[list["OauthToken"]] = relationship("OauthToken", lazy=True)
    queues: Mapped[list["Queue"]] = relationship("Queue", lazy=True)
    requests: Mapped[list["Request"]] = relationship("Request", lazy=True)
    beatmaps: Mapped[list["Beatmap"]] = relationship("Beatmap", lazy=True)
    beatmapsets: Mapped[list["Beatmapset"]] = relationship("Beatmapset", lazy=True)


class Role(Base):
    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)


class Profile(Base):
    __tablename__ = "profiles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=aware_utcnow, onupdate=aware_utcnow)

    # osu! API datastructure
    avatar_url: Mapped[Optional[str]] = mapped_column(String)
    username: Mapped[Optional[str]] = mapped_column(String)
    country_code: Mapped[Optional[str]] = mapped_column(String(2))
    graveyard_beatmapset_count: Mapped[Optional[int]] = mapped_column(Integer)
    loved_beatmapset_count: Mapped[Optional[int]] = mapped_column(Integer)
    pending_beatmapset_count: Mapped[Optional[int]] = mapped_column(Integer)
    ranked_beatmapset_count: Mapped[Optional[int]] = mapped_column(Integer)
    kudosu: Mapped[Optional[str]] = mapped_column(Text)
    is_restricted: Mapped[bool] = mapped_column(Boolean, default=False)

    # Hybrid annotations
    total_maps: Mapped[int]
    total_kudosu: Mapped[int]

    @hybrid_property
    def total_maps(self) -> int:
        return (
            (self.graveyard_beatmapset_count or 0) +
            (self.loved_beatmapset_count or 0) +
            (self.pending_beatmapset_count or 0) +
            (self.ranked_beatmapset_count or 0)
        )

    @total_maps.expression
    def total_maps(cls):
        return (
            func.coalesce(cls.graveyard_beatmapset_count, 0) +
            func.coalesce(cls.loved_beatmapset_count, 0) +
            func.coalesce(cls.pending_beatmapset_count, 0) +
            func.coalesce(cls.ranked_beatmapset_count, 0)
        )

    @hybrid_property
    def total_kudosu(self) -> int:
        return json.loads(self.kudosu)["total"] if self.kudosu else 0

    @total_kudosu.expression
    def total_kudosu(cls):
        return func.coalesce(cast(func.jsonb_extract_path_text(cast(cls.kudosu, JSONB), "total"), Integer), 0)


class ApiKey(Base):
    __tablename__ = "api_keys"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(32), unique=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=aware_utcnow)


class OauthToken(Base):
    __tablename__ = "oauth_tokens"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    access_token: Mapped[str] = mapped_column(String, nullable=False)
    refresh_token: Mapped[str] = mapped_column(String, nullable=False)
    expires_at: Mapped[int] = mapped_column(Integer, nullable=False)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=aware_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=aware_utcnow, onupdate=aware_utcnow)


class JWT(Base):
    __tablename__ = "jwts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    token: Mapped[str] = mapped_column(String, nullable=False)
    issued_at: Mapped[int] = mapped_column(Integer, nullable=False)
    expires_at: Mapped[int] = mapped_column(Integer, nullable=False)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=aware_utcnow, onupdate=aware_utcnow)


class ScoreFetcherTask(Base):
    __tablename__ = "score_fetcher_tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    last_fetch: Mapped[Optional[datetime]] = mapped_column(DateTime)


class ProfileFetcherTask(Base):
    __tablename__ = "profile_fetcher_tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    last_fetch: Mapped[Optional[datetime]] = mapped_column(DateTime)


class Beatmap(Base):
    __tablename__ = "beatmaps"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    beatmapset_id: Mapped[int] = mapped_column(Integer, ForeignKey("beatmapsets.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    leaderboards: Mapped[list["Leaderboard"]] = relationship("Leaderboard", lazy=True)
    snapshots: Mapped[list["BeatmapSnapshot"]] = relationship("BeatmapSnapshot", lazy=True)

    @hybrid_property
    def num_snapshots(self) -> int:
        return len(self.snapshots)

    @num_snapshots.expression
    def num_snapshots(cls):
        return (
            select(func.count(BeatmapSnapshot.id))
            .where(BeatmapSnapshot.beatmap_id == cls.id)
            .scalar_subquery()
        )


class BeatmapSnapshot(Base):
    __tablename__ = "beatmap_snapshots"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    beatmap_id: Mapped[int] = mapped_column(Integer, ForeignKey("beatmaps.id"), nullable=False)
    snapshot_number: Mapped[int] = mapped_column(Integer, nullable=False)
    snapshot_date: Mapped[datetime] = mapped_column(DateTime, default=aware_utcnow)
    checksum: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)

    # osu! API datastructure
    difficulty_rating: Mapped[float] = mapped_column(Float, nullable=False)
    mode: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    total_length: Mapped[int] = mapped_column(Integer, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    version: Mapped[str] = mapped_column(String, nullable=False)
    accuracy: Mapped[float] = mapped_column(Float, nullable=False)
    ar: Mapped[float] = mapped_column(Float, nullable=False)
    bpm: Mapped[int] = mapped_column(Integer, nullable=False)
    convert: Mapped[bool] = mapped_column(Boolean, nullable=False)
    count_circles: Mapped[int] = mapped_column(Integer, nullable=False)
    count_sliders: Mapped[int] = mapped_column(Integer, nullable=False)
    count_spinners: Mapped[int] = mapped_column(Integer, nullable=False)
    cs: Mapped[float] = mapped_column(Float, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    drain: Mapped[int] = mapped_column(Integer, nullable=False)
    hit_length: Mapped[int] = mapped_column(Integer, nullable=False)
    is_scoreable: Mapped[bool] = mapped_column(Boolean, nullable=False)
    last_updated: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    mode_int: Mapped[int] = mapped_column(Integer, nullable=False)
    passcount: Mapped[int] = mapped_column(Integer, nullable=False)
    playcount: Mapped[int] = mapped_column(Integer, nullable=False)
    ranked: Mapped[int] = mapped_column(Integer, nullable=False)
    url: Mapped[str] = mapped_column(String, nullable=False)

    # Relationships
    beatmapset_snapshots: Mapped[list["BeatmapsetSnapshot"]] = relationship("BeatmapsetSnapshot", secondary=beatmap_snapshot_beatmapset_snapshot_association, back_populates="beatmap_snapshots", lazy=True)
    leaderboard: Mapped["Leaderboard"] = relationship("Leaderboard", uselist=False, lazy=True)


class Beatmapset(Base):
    __tablename__ = "beatmapsets"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    snapshots: Mapped[list["BeatmapsetSnapshot"]] = relationship("BeatmapsetSnapshot", lazy=True)

    @hybrid_property
    def num_snapshots(self) -> int:
        return len(self.snapshots)

    @num_snapshots.expression
    def num_snapshots(cls):
        return (
            select(func.count(BeatmapsetSnapshot.id))
            .where(BeatmapsetSnapshot.beatmapset_id == cls.id)
            .scalar_subquery()
        )


class BeatmapsetSnapshot(Base):
    __tablename__ = "beatmapset_snapshots"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    beatmapset_id: Mapped[int] = mapped_column(Integer, ForeignKey("beatmapsets.id"), nullable=False)
    snapshot_number: Mapped[int] = mapped_column(Integer, nullable=False)
    snapshot_date: Mapped[datetime] = mapped_column(DateTime, default=aware_utcnow)
    checksum: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # osu! API datastructure
    artist: Mapped[str] = mapped_column(String, nullable=False)
    artist_unicode: Mapped[str] = mapped_column(String, nullable=False)
    covers: Mapped[str] = mapped_column(Text, nullable=False)
    creator: Mapped[str] = mapped_column(String, nullable=False)
    favourite_count: Mapped[int] = mapped_column(Integer, nullable=False)
    hype: Mapped[Optional[str]] = mapped_column(Text)
    nsfw: Mapped[bool] = mapped_column(Boolean, nullable=False)
    offset: Mapped[int] = mapped_column(Integer, nullable=False)
    play_count: Mapped[int] = mapped_column(Integer, nullable=False)
    preview_url: Mapped[str] = mapped_column(String, nullable=False)
    source: Mapped[str] = mapped_column(String, nullable=False)
    spotlight: Mapped[bool] = mapped_column(Boolean, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    title_unicode: Mapped[str] = mapped_column(String, nullable=False)
    track_id: Mapped[Optional[int]] = mapped_column(Integer)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    video: Mapped[bool] = mapped_column(Boolean, nullable=False)

    # Relationships
    beatmap_snapshots: Mapped[list["BeatmapSnapshot"]] = relationship(
        "BeatmapSnapshot",
        secondary=beatmap_snapshot_beatmapset_snapshot_association,
        back_populates="beatmapset_snapshots",
        lazy=True
    )
    tags: Mapped[list["Tag"]] = relationship(
        "Tag",
        secondary=tag_beatmapset_snapshot_association,
        lazy=True
    )
    user_profile: Mapped["Profile"] = relationship(
        "Profile",
        primaryjoin="foreign(BeatmapsetSnapshot.user_id) == remote(Profile.user_id)",
        uselist=False,
        overlaps="beatmapset_snapshots",
        lazy=True
    )

    # Hybrid annotations
    sr_gaps: Mapped[list[float]]
    num_difficulties: Mapped[int]

    @hybrid_property
    def num_difficulties(self) -> int:
        return len(self.beatmap_snapshots)

    @num_difficulties.expression
    def num_difficulties(cls):
        from app.database.ctes.num_difficulties import num_difficulties_cte

        return (
            select(num_difficulties_cte.c.target)
            .where(num_difficulties_cte.c.beatmapset_snapshot_id == cls.id)
            .scalar_subquery()
        )

    @hybrid_property
    def sr_gaps(self) -> list[float]:
        if not self.beatmap_snapshots:
            raise AttributeError(f"There are no beatmap_snapshots in BeatmapsetSnapshot {self.id}")

        ratings = sorted([snapshot.difficulty_rating for snapshot in self.beatmap_snapshots])
        diffs = [round(abs(ratings[i] - ratings[i + 1]), 2) for i in range(len(ratings) - 1)]

        return diffs if len(ratings) > 1 else []

    @sr_gaps.expression
    def sr_gaps(cls):
        from app.database.ctes.sr_gap import sr_gap_agg_cte

        return (
            select(sr_gap_agg_cte.c.sr_gap_agg)
            .where(sr_gap_agg_cte.c.beatmapset_snapshot_id == cls.id)
            .scalar_subquery()
        )


class BeatmapsetListing(Base):
    __tablename__ = "beatmapset_listings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    beatmapset_id: Mapped[int] = mapped_column(Integer, ForeignKey("beatmapsets.id"), nullable=False)
    beatmapset_snapshot_id: Mapped[int] = mapped_column(Integer, ForeignKey("beatmapset_snapshots.id"), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=aware_utcnow, onupdate=aware_utcnow)

    # Relationships
    beatmapset_snapshot: Mapped["BeatmapsetSnapshot"] = relationship("BeatmapsetSnapshot", primaryjoin="BeatmapsetListing.beatmapset_snapshot_id == BeatmapsetSnapshot.id", uselist=False)

    __table_args__ = (
        UniqueConstraint("beatmapset_id", "beatmapset_snapshot_id", name="_beatmapset_and_snapshot_uc"),
    )


class Leaderboard(Base):
    __tablename__ = "leaderboards"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    beatmap_id: Mapped[int] = mapped_column(Integer, ForeignKey("beatmaps.id"), nullable=False)
    beatmap_snapshot_id: Mapped[int] = mapped_column(Integer, ForeignKey("beatmap_snapshots.id"), nullable=False)

    # Relationships
    scores: Mapped[list["Score"]] = relationship("Score", lazy=True)

    __table_args__ = (
        UniqueConstraint("beatmap_id", "beatmap_snapshot_id", name="_beatmap_and_snapshot_uc"),
    )


class Score(Base):
    __tablename__ = "scores"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    beatmap_id: Mapped[int] = mapped_column(Integer, ForeignKey("beatmaps.id"), nullable=False)
    beatmapset_id: Mapped[int] = mapped_column(Integer, ForeignKey("beatmapsets.id"), nullable=False)
    leaderboard_id: Mapped[int] = mapped_column(Integer, ForeignKey("leaderboards.id"), nullable=False)

    # osu! API datastructure
    accuracy: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    max_combo: Mapped[int] = mapped_column(Integer, nullable=False)
    mode: Mapped[str] = mapped_column(String, nullable=False)
    mode_int: Mapped[int] = mapped_column(Integer, nullable=False)
    mods: Mapped[str] = mapped_column(Text, nullable=False)
    perfect: Mapped[bool] = mapped_column(Boolean, nullable=False)
    pp: Mapped[Optional[float]] = mapped_column(Float)
    rank: Mapped[str] = mapped_column(String, nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    statistics: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)

    __table_args__ = (
        UniqueConstraint("beatmap_id", "created_at", name="_beatmap_and_creation_time_uc"),
    )


class Queue(Base):
    __tablename__ = "queues"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=aware_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=aware_utcnow, onupdate=aware_utcnow)
    is_open: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    requests: Mapped[list["Request"]] = relationship(
        "Request",
        back_populates="queue",
        overlaps="queue",
        lazy=True
    )
    managers: Mapped[list["User"]] = relationship(
        "User",
        secondary=queue_manager_association,
        backref="managed_queues",
        lazy=True
    )
    user_profile: Mapped["Profile"] = relationship(
        "Profile",
        primaryjoin="foreign(Queue.user_id) == remote(Profile.user_id)",
        uselist=False,
        overlaps="queues",
        lazy=True
    )
    manager_profiles: Mapped[list["Profile"]] = relationship(
        "Profile",
        secondary=queue_manager_association,
        primaryjoin="Queue.id == queue_manager_association.c.queue_id",
        secondaryjoin="and_(User.id == queue_manager_association.c.user_id, User.id == Profile.user_id)",
        viewonly=True,
        lazy=True
    )

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="_user_and_name_uc"),
    )


class Request(Base):
    __tablename__ = "requests"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    beatmapset_id: Mapped[int] = mapped_column(Integer, ForeignKey("beatmapsets.id"), nullable=False)
    queue_id: Mapped[int] = mapped_column(Integer, ForeignKey("queues.id"), nullable=False)
    comment: Mapped[str] = mapped_column(Text)
    mv_checked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=aware_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=aware_utcnow, onupdate=aware_utcnow)
    status: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    user_profile: Mapped["Profile"] = relationship(
        "Profile",
        primaryjoin="foreign(Request.user_id) == remote(Profile.user_id)",
        uselist=False,
        overlaps="requests",
        lazy=True
    )
    queue: Mapped["Queue"] = relationship(
        "Queue",
        back_populates="requests",
        overlaps="requests",
        lazy=True
    )


class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)


class ModelClass(Enum):
    USER = User
    ROLE = Role
    PROFILE = Profile
    API_KEY = ApiKey
    OAUTH_TOKEN = OauthToken
    JWT = JWT
    SCORE_FETCHER_TASK = ScoreFetcherTask
    PROFILE_FETCHER_TASK = ProfileFetcherTask
    BEATMAP = Beatmap
    BEATMAP_SNAPSHOT = BeatmapSnapshot
    BEATMAPSET = Beatmapset
    BEATMAPSET_SNAPSHOT = BeatmapsetSnapshot
    BEATMAPSET_LISTING = BeatmapsetListing
    LEADERBOARD = Leaderboard
    SCORE = Score
    QUEUE = Queue
    REQUEST = Request
    TAG = Tag

    def get_required_columns(self) -> list[str]:
        required_columns = []

        for column in self.mapper.columns:
            if (
                not column.primary_key and not column.nullable and column.default is None
                or column.primary_key and not column.autoincrement
            ):
                required_columns.append(column.name)

        return required_columns

    @property
    def value(self) -> type[BaseType]:
        return self._value_

    @property
    def mapper(self) -> Mapper[BaseType]:
        return inspect(self.value)
