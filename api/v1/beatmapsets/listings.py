from app import cr
from app.schemas import beatmapset_listings_schema


def search(**kwargs):
    beatmap_listings = cr.get_beatmapset_listings(**kwargs)
    return beatmapset_listings_schema.dump(beatmap_listings), 200
