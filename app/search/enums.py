from enum import Enum
from typing import Callable

from sqlalchemy.sql.operators import eq, gt, lt, ge, le, ne
from sqlalchemy.sql import asc, desc
from sqlalchemy.orm.attributes import InstrumentedAttribute

from app.database.models import ModelClass, Profile, BeatmapSnapshot, BeatmapsetSnapshot, Request
from app.database.ctes.hashable_cte import HashableCTE
from app.database.ctes.sr_gap import min_sr_gap_cte, max_sr_gap_cte, avg_sr_gap_cte
from app.database.ctes.num_difficulties import num_difficulties_cte
from app.database.ctes.bms_ss.sr_gap import min_sr_gap_cte, max_sr_gap_cte, avg_sr_gap_cte
from app.database.ctes.bms_ss.num_difficulties import num_difficulties_cte


class SortOrder(Enum):
    ASCENDING = "asc"
    DESCENDING = "desc"

    @property
    def sort_func(self) -> Callable:
        return asc if self is SortOrder.ASCENDING else desc


class FilterName(Enum):
    MAPPER = ModelClass.PROFILE
    BEATMAP = ModelClass.BEATMAP_SNAPSHOT
    BEATMAPSET = ModelClass.BEATMAPSET_SNAPSHOT
    REQUEST = ModelClass.REQUEST


class FilterOperator(Enum):
    EQ = eq
    NEQ = ne
    GT = gt
    LT = lt
    GTE = ge
    LTE = le


class AdvancedFilterField(Enum):
    SR_GAPS = {
        "min": min_sr_gap_cte,
        "max": max_sr_gap_cte,
        "avg": avg_sr_gap_cte
    }
    NUM_DIFFICULTIES = num_difficulties_cte


class SortingField(Enum):
    # Profile fields
    PROFILE__COUNTRY_CODE = ModelClass.PROFILE, Profile.country_code
    PROFILE__GRAVEYARD_BEATMAPSET_COUNT = ModelClass.PROFILE, Profile.graveyard_beatmapset_count
    PROFILE__LOVED_BEATMAPSET_COUNT = ModelClass.PROFILE, Profile.loved_beatmapset_count
    PROFILE__PENDING_BEATMAPSET_COUNT = ModelClass.PROFILE, Profile.pending_beatmapset_count
    PROFILE__RANKED_BEATMAPSET_COUNT = ModelClass.PROFILE, Profile.ranked_beatmapset_count
    PROFILE__TOTAL_MAPS = ModelClass.PROFILE, Profile.total_maps
    PROFILE__TOTAL_KUDOSU = ModelClass.PROFILE, Profile.total_kudosu

    # BeatmapSnapshot fields
    BEATMAPSNAPSHOT__BEATMAP_ID = ModelClass.BEATMAP_SNAPSHOT, BeatmapSnapshot.beatmap_id
    BEATMAPSNAPSHOT__USER_ID = ModelClass.BEATMAP_SNAPSHOT, BeatmapSnapshot.user_id
    BEATMAPSNAPSHOT__DIFFICULTY_RATING = ModelClass.BEATMAP_SNAPSHOT, BeatmapSnapshot.difficulty_rating
    BEATMAPSNAPSHOT__MODE = ModelClass.BEATMAP_SNAPSHOT, BeatmapSnapshot.mode
    BEATMAPSNAPSHOT__TOTAL_LENGTH = ModelClass.BEATMAP_SNAPSHOT, BeatmapSnapshot.total_length
    BEATMAPSNAPSHOT__VERSION = ModelClass.BEATMAP_SNAPSHOT, BeatmapSnapshot.version
    BEATMAPSNAPSHOT__ACCURACY = ModelClass.BEATMAP_SNAPSHOT, BeatmapSnapshot.accuracy
    BEATMAPSNAPSHOT__AR = ModelClass.BEATMAP_SNAPSHOT, BeatmapSnapshot.ar
    BEATMAPSNAPSHOT__BPM = ModelClass.BEATMAP_SNAPSHOT, BeatmapSnapshot.bpm
    BEATMAPSNAPSHOT__COUNT_CIRCLES = ModelClass.BEATMAP_SNAPSHOT, BeatmapSnapshot.count_circles
    BEATMAPSNAPSHOT__COUNT_SLIDERS = ModelClass.BEATMAP_SNAPSHOT, BeatmapSnapshot.count_sliders
    BEATMAPSNAPSHOT__COUNT_SPINNERS = ModelClass.BEATMAP_SNAPSHOT, BeatmapSnapshot.count_spinners
    BEATMAPSNAPSHOT__CS = ModelClass.BEATMAP_SNAPSHOT, BeatmapSnapshot.cs
    BEATMAPSNAPSHOT__DRAIN = ModelClass.BEATMAP_SNAPSHOT, BeatmapSnapshot.drain
    BEATMAPSNAPSHOT__LAST_UPDATED = ModelClass.BEATMAP_SNAPSHOT, BeatmapSnapshot.last_updated
    BEATMAPSNAPSHOT__PASSCOUNT = ModelClass.BEATMAP_SNAPSHOT, BeatmapSnapshot.passcount
    BEATMAPSNAPSHOT__PLAYCOUNT = ModelClass.BEATMAP_SNAPSHOT, BeatmapSnapshot.playcount

    # BeatmapsetSnapshot fields
    BEATMAPSETSNAPSHOT__BEATMAPSET_ID = ModelClass.BEATMAPSET_SNAPSHOT, BeatmapsetSnapshot.beatmapset_id
    BEATMAPSETSNAPSHOT__USER_ID = ModelClass.BEATMAPSET_SNAPSHOT, BeatmapsetSnapshot.user_id
    BEATMAPSETSNAPSHOT__ARTIST = ModelClass.BEATMAPSET_SNAPSHOT, BeatmapsetSnapshot.artist
    BEATMAPSETSNAPSHOT__ARTIST_UNICODE = ModelClass.BEATMAPSET_SNAPSHOT, BeatmapsetSnapshot.artist_unicode
    BEATMAPSETSNAPSHOT__CREATOR = ModelClass.BEATMAPSET_SNAPSHOT, BeatmapsetSnapshot.creator
    BEATMAPSETSNAPSHOT__FAVOURITE_COUNT = ModelClass.BEATMAPSET_SNAPSHOT, BeatmapsetSnapshot.favourite_count
    BEATMAPSETSNAPSHOT__OFFSET = ModelClass.BEATMAPSET_SNAPSHOT, BeatmapsetSnapshot.offset
    BEATMAPSETSNAPSHOT__PLAY_COUNT = ModelClass.BEATMAPSET_SNAPSHOT, BeatmapsetSnapshot.play_count
    BEATMAPSETSNAPSHOT__SOURCE = ModelClass.BEATMAPSET_SNAPSHOT, BeatmapsetSnapshot.source
    BEATMAPSETSNAPSHOT__STATUS = ModelClass.BEATMAPSET_SNAPSHOT, BeatmapsetSnapshot.status
    BEATMAPSETSNAPSHOT__TITLE = ModelClass.BEATMAPSET_SNAPSHOT, BeatmapsetSnapshot.title
    BEATMAPSETSNAPSHOT__TITLE_UNICODE = ModelClass.BEATMAPSET_SNAPSHOT, BeatmapsetSnapshot.title_unicode
    BEATMAPSETSNAPSHOT__TRACK_ID = ModelClass.BEATMAPSET_SNAPSHOT, BeatmapsetSnapshot.track_id
    BEATMAPSETSNAPSHOT__NUM_DIFFICULTIES = ModelClass.BEATMAPSET_SNAPSHOT, HashableCTE(num_difficulties_cte)
    BEATMAPSETSNAPSHOT__SR_GAPS__MIN = ModelClass.BEATMAPSET_SNAPSHOT, HashableCTE(min_sr_gap_cte)
    BEATMAPSETSNAPSHOT__SR_GAPS__MAX = ModelClass.BEATMAPSET_SNAPSHOT, HashableCTE(max_sr_gap_cte)
    BEATMAPSETSNAPSHOT__SR_GAPS__AVG = ModelClass.BEATMAPSET_SNAPSHOT, HashableCTE(avg_sr_gap_cte)

    # Request fields
    REQUEST__COMMENT = ModelClass.REQUEST, Request.comment
    REQUEST__MV_CHECKED = ModelClass.REQUEST, Request.mv_checked
    REQUEST__CREATED_AT = ModelClass.REQUEST, Request.created_at
    REQUEST__UPDATED_AT = ModelClass.REQUEST, Request.updated_at
    REQUEST__STATUS = ModelClass.REQUEST, Request.status

    def __init__(self, model_class: ModelClass, target: InstrumentedAttribute | HashableCTE):
        self._value_ = target
        self.model_class = model_class
