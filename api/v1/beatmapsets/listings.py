import json

from api.utils import prime_query_kwargs
from app import db
from app.database.schemas import BeatmapsetListingSchema
from app.beatmap_filter import BeatmapFilter


def search(**kwargs):
    prime_query_kwargs(kwargs)

    mapper_filter = json.loads(kwargs.pop("mapper_filter")) if "mapper_filter" in kwargs else None
    beatmapset_filter = json.loads(kwargs.pop("beatmapset_filter")) if "beatmapset_filter" in kwargs else None
    request_filter = json.loads(kwargs.pop("request_filter")) if "request_filter" in kwargs else None

    with db.session_scope() as session:
        bf = BeatmapFilter()
        bf.add_filters(mapper_filter=mapper_filter, beatmapset_filter=beatmapset_filter, request_filter=request_filter)
        beatmap_listings = bf.filter(session=session, **kwargs)

        beatmap_listings_data = BeatmapsetListingSchema(many=True, session=session).dump(beatmap_listings)

    return beatmap_listings_data, 200
