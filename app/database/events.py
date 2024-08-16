from sqlalchemy import event
from sqlalchemy.engine.base import Connection, Engine
from sqlalchemy.pool.base import ConnectionPoolEntry
from sqlalchemy.sql import select, insert, update
from sqlalchemy.orm.mapper import Mapper
from sqlalchemy.orm.attributes import AttributeEventToken

from app import rc
from app.redis import ChannelName
from app.config import POSTGRESQL_CONFIGURATION
from .models import User, Profile, ScoreFetcherTask, ProfileFetcherTask, BeatmapsetSnapshot, BeatmapsetListing

__all__ = [
    "user_after_insert",
    "beatmapset_snapshot_after_insert"
]

POSTGRESQL_BASE_URL = f"postgresql://{POSTGRESQL_CONFIGURATION["username"]}:***@{POSTGRESQL_CONFIGURATION["host"]}:{POSTGRESQL_CONFIGURATION["port"]}/{POSTGRESQL_CONFIGURATION["database"]}"


@event.listens_for(Engine, "first_connect")
def on_connect(dbapi_connection: Connection, connection_record: ConnectionPoolEntry):
    print(f"[{Engine.__name__}] Connected to PostgreSQL at '{POSTGRESQL_BASE_URL}'")


@event.listens_for(User, "after_insert")
def user_after_insert(mapper: Mapper[User], connection: Connection, target: User):
    insert_profile_stmt = (
        insert(Profile)
        .values(user_id=target.id)
    )

    insert_score_fetcher_stmt = (
        insert(ScoreFetcherTask)
        .values(user_id=target.id)
        .returning(ScoreFetcherTask.id)
    )

    insert_profile_fetcher_stmt = (
        insert(ProfileFetcherTask)
        .values(user_id=target.id)
        .returning(ProfileFetcherTask.id)
    )

    connection.execute(insert_profile_stmt)

    result = connection.execute(insert_score_fetcher_stmt)
    score_fetcher_task_id = result.scalar()

    result = connection.execute(insert_profile_fetcher_stmt)
    profile_fetcher_task_id = result.scalar()

    rc.publish(ChannelName.SCORE_FETCHER_TASKS.value, score_fetcher_task_id)
    rc.publish(ChannelName.PROFILE_FETCHER_TASKS.value, profile_fetcher_task_id)


@event.listens_for(ScoreFetcherTask.enabled, "set")
def score_fetcher_task_enabled_set(target: ScoreFetcherTask, value: bool, oldvalue: bool, initiator: AttributeEventToken):
    if value:
        rc.publish(ChannelName.SCORE_FETCHER_TASKS.value, target.id)


@event.listens_for(BeatmapsetSnapshot, "after_insert")
def beatmapset_snapshot_after_insert(mapper: Mapper[BeatmapsetSnapshot], connection: Connection, target: BeatmapsetSnapshot):

    select_stmt = (
        select(BeatmapsetListing)
        .where(BeatmapsetListing.beatmapset_id == target.beatmapset_id)
    )

    beatmapset_listing = connection.scalar(select_stmt)

    if not beatmapset_listing:
        insert_stmt = (
            insert(BeatmapsetListing)
            .values(beatmapset_id=target.beatmapset_id, beatmapset_snapshot_id=target.id)
        )

        connection.execute(insert_stmt)
    else:
        update_stmt = (
            update(BeatmapsetListing)
            .where(BeatmapsetListing.id == beatmapset_listing.id)
            .values(beatmapset_snapshot_id=target.id)
        )

        connection.execute(update_stmt)
