from typing import Iterable

from sqlalchemy.sql import select
from sqlalchemy.sql.selectable import CTE
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy.orm.attributes import InstrumentedAttribute

from app.database.models import BeatmapSnapshot, beatmap_snapshot_beatmapset_snapshot_association


def bm_ss_filtering_cte_factory(beatmap_snapshot_column: InstrumentedAttribute, aggregated_conditions: Iterable[BinaryExpression]) -> CTE:
    if not isinstance(beatmap_snapshot_column, InstrumentedAttribute):
        raise TypeError(f"Invalid BeatmapSnapshot column type: {type(beatmap_snapshot_column).__name__}. Must be InstrumentedAttribute")

    if beatmap_snapshot_column.class_ is not BeatmapSnapshot:
        raise ValueError(f"Column belongs to invalid model: {beatmap_snapshot_column.class_.__name__}. Must belong to BeatmapSnapshot")

    return (
        select(
            beatmap_snapshot_beatmapset_snapshot_association.c.beatmapset_snapshot_id,
            func.array_agg(beatmap_snapshot_column).label("target")
        )
        .join(
            BeatmapSnapshot,
            BeatmapSnapshot.id == beatmap_snapshot_beatmapset_snapshot_association.c.beatmap_snapshot_id
        )
        .group_by(beatmap_snapshot_beatmapset_snapshot_association.c.beatmapset_snapshot_id)
        .having(*aggregated_conditions)
        .cte(f"beatmap_snapshot_{beatmap_snapshot_column.name}_filter_cte")
    )
