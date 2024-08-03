import json

from app.schemas import beatmapset_listings_schema
from app.beatmap_filter import BeatmapFilter


def search(**kwargs):
    mapper_filter = json.loads(kwargs.pop("mapper_filter", "{}"))
    beatmapset_filter = json.loads(kwargs.pop("beatmapset_filter", "{}"))
    request_filter = json.loads(kwargs.pop("request_filter", "{}"))

    bf = BeatmapFilter()
    bf.add_filters(mapper_filter=mapper_filter, beatmapset_filter=beatmapset_filter, request_filter=request_filter)
    beatmap_listings = bf.filter(**kwargs)

    return beatmapset_listings_schema.dump(beatmap_listings), 200
