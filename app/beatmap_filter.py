from sqlalchemy import select, func, desc
from sqlalchemy.orm import aliased

from app import db, cr
from app.models import BeatmapsetSnapshot, Request, BeatmapsetListing


class BeatmapFilter:
    def __init__(self):
        self.filters: dict[str: dict] = {}

    def add_filters(self, mapper_filter: dict | None = None, beatmapset_filter: dict | None = None, request_filter: dict | None = None):
        if mapper_filter is not None:
            self.mapper_filter = mapper_filter
        if beatmapset_filter is not None:
            self.beatmapset_filter = beatmapset_filter
        if request_filter is not None:
            self.request_filter = request_filter

    def filter(self, **kwargs) -> list[BeatmapsetListing]:
        # TODO: Come up with a good way to combine filters using CTEs, this is just a workaround for now

        if self.request_filter and "user_id" in self.request_filter:
            return self.my_requests(self.request_filter["user_id"]["eq"])

        if self.request_filter is not None:
            return self.all_requests()

        return cr.get_beatmapset_listings(**kwargs)

    def all_requests(self) -> list[BeatmapsetListing]:
        subquery = select(Request.beatmapset_id, Request.id.label("request_id")).subquery()

        query = (
            select(BeatmapsetListing)
            .join(subquery, BeatmapsetListing.beatmapset_id == subquery.c.beatmapset_id)
            .order_by(desc(subquery.c.request_id))
        )

        result = db.session.execute(query).scalars()
        return result

    def my_requests(self, user_id: int) -> list[BeatmapsetListing]:
        subquery = (
            select(Request.beatmapset_id, Request.id.label("request_id"))
            .where(Request.user_id == user_id).subquery()
        )

        latest_snapshot = aliased(BeatmapsetSnapshot, name="latest_snapshot")
        beatmapset_listing_alias = aliased(BeatmapsetListing, name="beatmapset_listing")

        latest_snapshot_subquery = (
            select(
                BeatmapsetSnapshot.beatmapset_id,
                func.max(BeatmapsetSnapshot.id).label("latest_id")
            )
            .where(BeatmapsetSnapshot.beatmapset_id.in_(select(subquery.c.beatmapset_id)))
            .group_by(BeatmapsetSnapshot.beatmapset_id)
            .subquery()
        )

        query = (
            select(beatmapset_listing_alias)
            .join(
                latest_snapshot,
                latest_snapshot.id == beatmapset_listing_alias.beatmapset_snapshot_id
            )
            .join(
                latest_snapshot_subquery,
                latest_snapshot.id == latest_snapshot_subquery.c.latest_id
            )
            .join(
                subquery,
                latest_snapshot.beatmapset_id == subquery.c.beatmapset_id
            )
            .order_by(desc(subquery.c.request_id))
        )

        result = db.session.execute(query).scalars()
        return result

    @property
    def mapper_filter(self) -> dict | None:
        return self.filters.get("mapper_filter")

    @mapper_filter.setter
    def mapper_filter(self, mapper_filter_: dict | None):
        self.filters["mapper_filter"] = mapper_filter_

    @property
    def beatmapset_filter(self) -> dict | None:
        return self.filters.get("beatmapset_filter")

    @beatmapset_filter.setter
    def beatmapset_filter(self, beatmapset_filter_: dict | None):
        self.filters["beatmapset_filter"] = beatmapset_filter_

    @property
    def request_filter(self) -> dict | None:
        return self.filters.get("request_filter")

    @request_filter.setter
    def request_filter(self, request_filter_: dict | None):
        self.filters["request_filter"] = request_filter_
