from sqlalchemy import event
from sqlalchemy.engine.base import Connection, Engine
from sqlalchemy.pool.base import ConnectionPoolEntry
from sqlalchemy.sql import select, insert, update
from sqlalchemy.orm.mapper import Mapper as Mapper_

from app import rc
from app.redis import ChannelName
from app.config import POSTGRESQL_CONFIGURATION
from .models import User, Mapper, ScoreFetcherTask, MapperInfoFetcherTask, BeatmapsetSnapshot, BeatmapsetListing

__all__ = [
    "user_after_insert",
    "mapper_after_insert",
    "beatmapset_snapshot_after_insert"
]

POSTGRESQL_BASE_URL = f"postgresql://{POSTGRESQL_CONFIGURATION["username"]}:***@{POSTGRESQL_CONFIGURATION["host"]}:{POSTGRESQL_CONFIGURATION["port"]}/{POSTGRESQL_CONFIGURATION["database"]}"


@event.listens_for(Engine, "first_connect")
def on_connect(dbapi_connection: Connection, connection_record: ConnectionPoolEntry):
    print(f"[{Engine.__name__}] Connected to PostgreSQL at '{POSTGRESQL_BASE_URL}'")


@event.listens_for(User, "after_insert")
def user_after_insert(mapper: Mapper_[User], connection: Connection, target: User):
    insert_stmt = (
        insert(ScoreFetcherTask)
        .values(user_id=target.id)
        .returning(ScoreFetcherTask.id)
    )

    result = connection.execute(insert_stmt)
    task_id = result.scalar()

    rc.publish(ChannelName.SCORE_FETCHER_TASKS.value, task_id)


@event.listens_for(Mapper, "after_insert")
def mapper_after_insert(mapper: Mapper_[Mapper], connection: Connection, target: Mapper):
    insert_stmt = (
        insert(MapperInfoFetcherTask)
        .values(mapper_id=target.id)
        .returning(MapperInfoFetcherTask.id)
    )

    result = connection.execute(insert_stmt)
    task_id = result.scalar()

    rc.publish(ChannelName.SCORE_FETCHER_TASKS.value, task_id)


@event.listens_for(BeatmapsetSnapshot, "after_insert")
def beatmapset_snapshot_after_insert(mapper: Mapper_[BeatmapsetSnapshot], connection: Connection, target: BeatmapsetSnapshot):

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
