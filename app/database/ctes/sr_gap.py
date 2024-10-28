from sqlalchemy.sql import select
from sqlalchemy.sql.sqltypes import Numeric, Float
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.expression import cast

from app.database.models import BeatmapSnapshot, beatmap_snapshot_beatmapset_snapshot_association

bms_ss_with_multiple_bm_ss_cte = (
    select(
        beatmap_snapshot_beatmapset_snapshot_association.c.beatmapset_snapshot_id,
        func.count(beatmap_snapshot_beatmapset_snapshot_association.c.beatmap_snapshot_id).label("snapshot_count")
    )
    .join(
        BeatmapSnapshot,
        BeatmapSnapshot.id == beatmap_snapshot_beatmapset_snapshot_association.c.beatmap_snapshot_id
    )
    .group_by(beatmap_snapshot_beatmapset_snapshot_association.c.beatmapset_snapshot_id)
    .having(func.count(beatmap_snapshot_beatmapset_snapshot_association.c.beatmap_snapshot_id) > 1)
    .cte("count_cte")
)

sr_gap_cte = (
    select(
        beatmap_snapshot_beatmapset_snapshot_association.c.beatmapset_snapshot_id,
        cast(
            func.round(
                func.abs(
                    cast(BeatmapSnapshot.difficulty_rating, Numeric) -
                    func.lag(cast(BeatmapSnapshot.difficulty_rating, Numeric))
                    .over(
                        partition_by=beatmap_snapshot_beatmapset_snapshot_association.c.beatmapset_snapshot_id,
                        order_by=BeatmapSnapshot.difficulty_rating
                    )
                ),
                2
            ),
            Float
        ).label("sr_gap")
    )
    .join(
        beatmap_snapshot_beatmapset_snapshot_association,
        BeatmapSnapshot.id == beatmap_snapshot_beatmapset_snapshot_association.c.beatmap_snapshot_id
    )
    .join(
        bms_ss_with_multiple_bm_ss_cte,
        bms_ss_with_multiple_bm_ss_cte.c.beatmapset_snapshot_id == beatmap_snapshot_beatmapset_snapshot_association.c.beatmapset_snapshot_id
    )
    .cte("sr_gap_cte")
)

sr_gap_agg_cte = (
    select(
        sr_gap_cte.c.beatmapset_snapshot_id,
        func.array_agg(sr_gap_cte.c.sr_gap).label("sr_gap_agg")
    )
    .where(sr_gap_cte.c.sr_gap.isnot(None))
    .group_by(sr_gap_cte.c.beatmapset_snapshot_id)
    .cte("sr_gap_agg_cte")
)

min_sr_gap_cte = (
    select(
        sr_gap_cte.c.beatmapset_snapshot_id,
        func.min(sr_gap_cte.c.sr_gap).label("target")
    )
    .group_by(sr_gap_cte.c.beatmapset_snapshot_id)
    .cte("min_sr_gap_cte")
)

max_sr_gap_cte = (
    select(
        sr_gap_cte.c.beatmapset_snapshot_id,
        func.max(sr_gap_cte.c.sr_gap).label("target")
    )
    .group_by(sr_gap_cte.c.beatmapset_snapshot_id)
    .cte("max_sr_gap_cte")
)

avg_sr_gap_cte = (
    select(
        sr_gap_cte.c.beatmapset_snapshot_id,
        cast(
            func.round(
                cast(
                    func.avg(sr_gap_cte.c.sr_gap),
                    Numeric
                ),
                2
            ),
            Float
        ).label("target")
    )
    .group_by(sr_gap_cte.c.beatmapset_snapshot_id)
    .cte("avg_sr_gap_cte")
)
