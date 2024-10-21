from enum import Enum

from sqlalchemy.sql.operators import eq, gt, lt, ge, le, ne

from app.database.models import ModelClass


class FilterName(Enum):
    MAPPER = ModelClass.PROFILE
    BEATMAP = ModelClass.BEATMAP_SNAPSHOT
    BEATMAPSET = ModelClass.BEATMAPSET_SNAPSHOT
    REQUEST = ModelClass.REQUEST


class SortOrder(Enum):
    ASCENDING = "asc"
    DESCENDING = "desc"


class FilterOperator(Enum):
    EQ = eq
    GT = gt
    LT = lt
    GTE = ge
    LTE = le
    NEQ = ne
