from sqlalchemy.sql import select
from sqlalchemy.sql.selectable import CTE
from sqlalchemy.sql.functions import func
from sqlalchemy.orm.attributes import InstrumentedAttribute

from app.database.models import BeatmapsetSnapshot, Request
from app.search.enums import SortOrder


def request_sorting_cte_factory(request_column: InstrumentedAttribute, sort_order: SortOrder = SortOrder.ASCENDING) -> CTE:
    if not isinstance(request_column, InstrumentedAttribute):
        raise TypeError(f"Invalid Request column type: {type(request_column).__name__}. Must be InstrumentedAttribute")

    if request_column.class_ is not Request:
        raise ValueError(f"Column belongs to invalid model: {request_column.class_.__name__}. Must belong to Request")

    return (
        select(
            BeatmapsetSnapshot.id.label("beatmapset_snapshot_id"),
            request_column.label("target"),
            func.row_number().over(
                partition_by=BeatmapsetSnapshot.id,
                order_by=sort_order.sort_func(request_column)
            ).label("rank")
        )
        .join(
            Request,
            Request.beatmapset_id == BeatmapsetSnapshot.beatmapset_id
        )
        .cte(f"request_{request_column.name}_ranked_cte")
    )
