from typing import Any

from sqlalchemy.sql import select
from sqlalchemy.sql.selectable import CTE

from app.database.models import Profile, BeatmapsetSnapshot


def profile_filtering_cte_factory(profile_column: Any) -> CTE:
    if profile_column.class_ is not Profile:
        raise ValueError(f"Column belongs to invalid model: {profile_column.class_.__name__}. Must belong to Profile")

    column_name = str(profile_column).split(".")[-1]

    return (
        select(
            BeatmapsetSnapshot.id.label("beatmapset_snapshot_id"),
            profile_column.label("target")
        )
        .join(
            Profile,
            Profile.user_id == BeatmapsetSnapshot.user_id
        )
        .distinct(BeatmapsetSnapshot.id)
        .cte(f"profile_{column_name}_filter_cte")
    )
