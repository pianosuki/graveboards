from sqlalchemy import event, Connection
from sqlalchemy.orm import Mapper as Mapper_
from sqlalchemy.sql import update

from app import cr
from .models import BeatmapsetSnapshot, BeatmapsetListing, Request, Mapper, Queue, OauthToken
from .utils import aware_utcnow

__all__ = [
    "receive_after_insert"
]


@event.listens_for(BeatmapsetSnapshot, "after_insert")
def receive_after_insert(mapper: Mapper_, connection: Connection, target: BeatmapsetSnapshot):
    beatmapset_listing = cr.get_beatmapset_listing(beatmapset_id=target.beatmapset_id)

    if not beatmapset_listing:
        beatmap_listing = BeatmapsetListing(beatmapset_id=target.beatmapset_id, beatmapset_snapshot_id=target.id)

        insert_stmt = BeatmapsetListing.__table__.insert().values(
            beatmapset_id=beatmap_listing.beatmapset_id,
            beatmapset_snapshot_id=beatmap_listing.beatmapset_snapshot_id
        )

        connection.execute(insert_stmt)
    else:
        update_stmt = (
            update(BeatmapsetListing.__table__)
            .where(BeatmapsetListing.__table__.c.id == beatmapset_listing.id)
            .values(beatmapset_snapshot_id=target.id)
        )

        connection.execute(update_stmt)


@event.listens_for(Mapper, "before_update")
def receive_before_update(mapper: Mapper_, connection: Connection, target: Mapper):
    target.updated_at = aware_utcnow()


@event.listens_for(OauthToken, "before_update")
def receive_before_update(mapper: Mapper_, connection: Connection, target: OauthToken):
    target.updated_at = aware_utcnow()


@event.listens_for(BeatmapsetListing, "before_update")
def receive_before_update(mapper: Mapper_, connection: Connection, target: BeatmapsetListing):
    target.updated_at = aware_utcnow()


@event.listens_for(Queue, "before_update")
def receive_before_update(mapper: Mapper_, connection: Connection, target: Queue):
    target.updated_at = aware_utcnow()


@event.listens_for(Request, "before_update")
def receive_before_update(mapper: Mapper_, connection: Connection, target: Request):
    target.updated_at = aware_utcnow()






