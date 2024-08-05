import json

from app.schemas import beatmapset_listings_schema
from app.beatmap_filter import BeatmapFilter


def search(**kwargs):
    mapper_filter = json.loads(kwargs.pop("mapper_filter")) if "mapper_filter" in kwargs else None
    beatmapset_filter = json.loads(kwargs.pop("beatmapset_filter")) if "beatmapset_filter" in kwargs else None
    request_filter = json.loads(kwargs.pop("request_filter")) if "request_filter" in kwargs else None

    bf = BeatmapFilter()
    bf.add_filters(mapper_filter=mapper_filter, beatmapset_filter=beatmapset_filter, request_filter=request_filter)
    beatmap_listings = bf.filter(**kwargs)

    return beatmapset_listings_schema.dump(beatmap_listings), 200
