from sqlalchemy import event
from sqlalchemy.engine.base import Connection
from sqlalchemy.sql import select, insert, update, func
from sqlalchemy.orm.mapper import Mapper
from sqlalchemy.orm.attributes import AttributeEventToken

from app.redis import ChannelName, redis_connection
from .models import User, ScoreFetcherTask, ProfileFetcherTask, BeatmapsetSnapshot, BeatmapsetListing, BeatmapSnapshot


@event.listens_for(User, "after_insert")
def user_after_insert(mapper: Mapper[User], connection: Connection, target: User):
    insert_score_fetcher_stmt = (
        insert(ScoreFetcherTask)
        .values(user_id=target.id)
    )
    insert_profile_fetcher_stmt = (
        insert(ProfileFetcherTask)
        .values(user_id=target.id)
        .returning(ProfileFetcherTask.id)
    )

    connection.execute(insert_score_fetcher_stmt)
    result = connection.execute(insert_profile_fetcher_stmt)
    profile_fetcher_task_id = result.scalar()

    with redis_connection() as rc:
        rc.publish(ChannelName.PROFILE_FETCHER_TASKS.value, profile_fetcher_task_id)


@event.listens_for(ScoreFetcherTask.enabled, "set")
def score_fetcher_task_enabled_set(target: ScoreFetcherTask, value: bool, oldvalue: bool, initiator: AttributeEventToken):
    if value:
        with redis_connection() as rc:
            rc.publish(ChannelName.SCORE_FETCHER_TASKS.value, target.id)


@event.listens_for(BeatmapSnapshot, "before_insert")
def beatmap_snapshot_before_insert(mapper: Mapper[BeatmapSnapshot], connection: Connection, target: BeatmapSnapshot):
    select_stmt = (
        select(func.max(BeatmapSnapshot.snapshot_number))
        .where(BeatmapSnapshot.beatmap_id == target.beatmap_id)
    )

    latest_snapshot = connection.scalar(select_stmt)
    target.snapshot_number = (latest_snapshot or 0) + 1


@event.listens_for(BeatmapsetSnapshot, "before_insert")
def beatmapset_snapshot_before_insert(mapper: Mapper[BeatmapsetSnapshot], connection: Connection, target: BeatmapsetSnapshot):
    select_stmt = (
        select(func.max(BeatmapsetSnapshot.snapshot_number))
        .where(BeatmapsetSnapshot.beatmapset_id == target.beatmapset_id)
    )

    latest_snapshot = connection.scalar(select_stmt)
    target.snapshot_number = (latest_snapshot or 0) + 1


@event.listens_for(BeatmapsetSnapshot, "after_insert")
def beatmapset_snapshot_after_insert(mapper: Mapper[BeatmapsetSnapshot], connection: Connection, target: BeatmapsetSnapshot):
    select_stmt = (
        select(BeatmapsetListing.id)
        .where(BeatmapsetListing.beatmapset_id == target.beatmapset_id)
    )

    beatmapset_listing_id = connection.scalar(select_stmt)

    if not beatmapset_listing_id:
        insert_stmt = (
            insert(BeatmapsetListing)
            .values(beatmapset_id=target.beatmapset_id, beatmapset_snapshot_id=target.id)
        )

        connection.execute(insert_stmt)
    else:
        update_stmt = (
            update(BeatmapsetListing)
            .where(BeatmapsetListing.id == beatmapset_listing_id)
            .values(beatmapset_snapshot_id=target.id)
        )

        connection.execute(update_stmt)
