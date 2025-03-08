from typing import Any

from sqlalchemy.sql import select
from sqlalchemy.sql.selectable import CTE
from sqlalchemy.sql.functions import func

from app.database.models import Profile, BeatmapsetSnapshot
from app.search.enums import SortOrder


def profile_sorting_cte_factory(profile_column: Any, sort_order: SortOrder = SortOrder.ASCENDING) -> CTE:
    if profile_column.class_ is not Profile:
        raise ValueError(f"Column belongs to invalid model: {profile_column.class_.__name__}. Must belong to Profile")

    column_name = str(profile_column).split(".")[-1]

    return (
        select(
            BeatmapsetSnapshot.id.label("beatmapset_snapshot_id"),
            profile_column.label("target"),
            func.row_number().over(
                partition_by=BeatmapsetSnapshot.id,
                order_by=sort_order.sort_func(profile_column)
            ).label("rank")
        )
        .join(
            Profile,
            Profile.user_id == BeatmapsetSnapshot.user_id
        )
        .distinct(BeatmapsetSnapshot.id)
        .cte(f"profile_{column_name}_ranked_cte")
    )
