from enum import Enum

from sqlalchemy.sql.operators import eq, gt, lt, ge, le, ne

from app.database.models import ModelClass
from app.database.ctes.sr_gap import min_sr_gap_cte, max_sr_gap_cte, avg_sr_gap_cte
from app.database.ctes.num_difficulties import num_difficulties_cte


class SortOrder(Enum):
    ASCENDING = "asc"
    DESCENDING = "desc"


class FilterName(Enum):
    MAPPER = ModelClass.PROFILE
    BEATMAP = ModelClass.BEATMAP_SNAPSHOT
    BEATMAPSET = ModelClass.BEATMAPSET_SNAPSHOT
    REQUEST = ModelClass.REQUEST


class FilterOperator(Enum):
    EQ = eq
    GT = gt
    LT = lt
    GTE = ge
    LTE = le
    NEQ = ne


class AdvancedFilterField(Enum):
    SR_GAPS = {
        "min": min_sr_gap_cte,
        "max": max_sr_gap_cte,
        "avg": avg_sr_gap_cte
    }
    NUM_DIFFICULTIES = num_difficulties_cte
