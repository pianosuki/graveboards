from sqlalchemy.sql import select
from sqlalchemy.sql.selectable import CTE
from sqlalchemy.sql.functions import func
from sqlalchemy.orm.attributes import InstrumentedAttribute

from app.database.models import BeatmapSnapshot, BeatmapsetSnapshot, beatmap_snapshot_beatmapset_snapshot_association
from app.search.enums import SortOrder


def bm_ss_sorting_cte_factory(beatmap_snapshot_column: InstrumentedAttribute, sort_order: SortOrder = SortOrder.ASCENDING) -> CTE:
    if not isinstance(beatmap_snapshot_column, InstrumentedAttribute):
        raise TypeError(f"Invalid BeatmapSnapshot column type: {type(beatmap_snapshot_column).__name__}. Must be InstrumentedAttribute")

    if beatmap_snapshot_column.class_ is not BeatmapSnapshot:
        raise ValueError(f"Column belongs to invalid model: {beatmap_snapshot_column.class_.__name__}. Must belong to BeatmapSnapshot")

    return (
        select(
            BeatmapsetSnapshot.id.label("beatmapset_snapshot_id"),
            BeatmapSnapshot.id.label("beatmap_snapshot_id"),
            beatmap_snapshot_column.label("target"),
            func.row_number().over(
                partition_by=BeatmapsetSnapshot.id,
                order_by=sort_order.sort_func(beatmap_snapshot_column)
            ).label("rank")
        )
        .join(
            beatmap_snapshot_beatmapset_snapshot_association,
            beatmap_snapshot_beatmapset_snapshot_association.c.beatmap_snapshot_id == BeatmapSnapshot.id
        )
        .join(
            BeatmapsetSnapshot,
            BeatmapsetSnapshot.id == beatmap_snapshot_beatmapset_snapshot_association.c.beatmapset_snapshot_id
        )
        .cte(f"beatmap_snapshot_{beatmap_snapshot_column.name}_ranked_cte")
    )
