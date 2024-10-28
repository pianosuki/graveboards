from sqlalchemy.sql import select, or_
from sqlalchemy.sql.selectable import CTE

from app.database.models import BeatmapSnapshot, BeatmapsetSnapshot, beatmap_snapshot_beatmapset_snapshot_association


def search_filter_cte_factory(search_query: str) -> CTE:
    return (
        select(
            beatmap_snapshot_beatmapset_snapshot_association.c.beatmapset_snapshot_id
        )
        .join(
            BeatmapsetSnapshot,
            BeatmapsetSnapshot.id == beatmap_snapshot_beatmapset_snapshot_association.c.beatmapset_snapshot_id
        )
        .join(
            BeatmapSnapshot,
            BeatmapSnapshot.id == beatmap_snapshot_beatmapset_snapshot_association.c.beatmap_snapshot_id
        )
        .where(
            or_(
                BeatmapSnapshot.version.ilike(f"%{search_query}%"),
                BeatmapsetSnapshot.artist.ilike(f"%{search_query}%"),
                BeatmapsetSnapshot.artist_unicode.ilike(f"%{search_query}%"),
                BeatmapsetSnapshot.title.ilike(f"%{search_query}%"),
                BeatmapsetSnapshot.title_unicode.ilike(f"%{search_query}%"),
                BeatmapsetSnapshot.creator.ilike(f"%{search_query}%"),
                BeatmapsetSnapshot.source.ilike(f"%{search_query}%")
            )
        )
        .distinct(beatmap_snapshot_beatmapset_snapshot_association.c.beatmapset_snapshot_id)
        .cte("search_filter_cte")
    )
