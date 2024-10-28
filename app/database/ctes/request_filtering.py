from typing import Any

from sqlalchemy.sql import select
from sqlalchemy.sql.selectable import CTE

from app.database.models import Request, BeatmapsetSnapshot


def request_filtering_cte_factory(request_column: Any) -> CTE:
    if request_column.class_ is not Request:
        raise ValueError(f"Column belongs to invalid model: {request_column.class_.__name__}. Must belong to Request")

    column_name = str(request_column).split(".")[-1]

    return (
        select(
            BeatmapsetSnapshot.id.label("beatmapset_snapshot_id"),
            request_column.label("target")
        )
        .join(
            Request,
            Request.beatmapset_id == BeatmapsetSnapshot.beatmapset_id
        )
        .distinct(BeatmapsetSnapshot.id)
        .cte(f"request_{column_name}_filter_cte")
    )
