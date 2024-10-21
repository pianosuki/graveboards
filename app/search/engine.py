import json
from typing import Literal, Generator

from sqlalchemy.sql import select, and_, or_, asc, desc
from sqlalchemy.sql.selectable import Select
from sqlalchemy.orm.session import Session
from sqlalchemy.orm.strategy_options import joinedload

from app.database.models import User, Profile, Beatmap, BeatmapSnapshot, Beatmapset, BeatmapsetSnapshot, BeatmapsetListing, Queue, Request, ModelClass
from .enums import FilterName, SortOrder, FilterOperator

PaginatedResultsGenerator = Generator[list[BeatmapsetListing], Session, None]
FilterDict = dict[str, dict]


class SearchEngine:
    def __init__(self):
        self._search_query: str = ""
        self._sort_by: str = ""
        self._sort_order: SortOrder = SortOrder.ASCENDING
        self._filters: dict[FilterName, FilterDict] = {filter_name: {} for filter_name in FilterName}
        self._queue_id: int | None = None
        self._limit: int = 50
        self._offset: int = 0

    def search(
        self,
        search_query: str = None,
        sort_by: str = None,
        sort_order: str = None,
        mapper_filter: str = None,
        beatmap_filter: str = None,
        beatmapset_filter: str = None,
        request_filter: str = None,
        queue_id: int = None,
        limit: int = None,
        offset: int = None
    ) -> PaginatedResultsGenerator:
        if search_query:
            self.search_query = search_query
        if sort_by:
            self.sort_by = sort_by
        if sort_order:
            self.sort_order = sort_order
        if mapper_filter:
            self.mapper_filter = mapper_filter
        if beatmap_filter:
            self.beatmap_filter = beatmap_filter
        if beatmapset_filter:
            self.beatmapset_filter = beatmapset_filter
        if request_filter:
            self.request_filter = request_filter
        if queue_id:
            self.queue_id = queue_id
        if limit:
            self._limit = limit
        if offset:
            self._offset = offset

        query = self._compile_query()

        return self._results_generator(query)

    def _results_generator(self, query: Select) -> PaginatedResultsGenerator:
        while True:
            page_query = query.limit(self._limit).offset(self._offset)

            session: Session = yield
            results = session.execute(page_query).scalars().all()

            if not results:
                break

            yield results

            self._offset += self._limit

    def _compile_query(self) -> Select:
        query = (
            select(BeatmapsetListing)
            .join(Beatmapset)
            .join(BeatmapsetSnapshot, BeatmapsetSnapshot.beatmapset_id == Beatmapset.id )
            .join(Beatmap, Beatmap.beatmapset_id == Beatmapset.id)
            .join(BeatmapSnapshot, BeatmapSnapshot.beatmap_id == Beatmap.id)
            .join(User, User.id == Beatmapset.user_id)
            .join(Profile, Profile.user_id == User.id)
            .join(Request, Request.beatmapset_id == Beatmapset.id)
        )

        if self._queue_id:
            request_cte = (
                select(Request.beatmapset_id)
                .join(Queue)
                .where(Queue.id == self._queue_id)
                .cte("request_cte")
            )

            query = query.join(request_cte, Beatmapset.id == request_cte.c.beatmapset_id)

        if self._search_query:
            search_filter = or_(
                BeatmapSnapshot.version.ilike(f"%{self._search_query}%"),
                BeatmapsetSnapshot.artist.ilike(f"%{self._search_query}%"),
                BeatmapsetSnapshot.artist_unicode.ilike(f"%{self._search_query}%"),
                BeatmapsetSnapshot.title.ilike(f"%{self._search_query}%"),
                BeatmapsetSnapshot.title_unicode.ilike(f"%{self._search_query}%"),
                BeatmapsetSnapshot.creator.ilike(f"%{self._search_query}%"),
                BeatmapsetSnapshot.source.ilike(f"%{self._search_query}%")
            )

            query = query.where(search_filter)

        for filter_name in FilterName:
            if self._filters[filter_name]:
                query = self._apply_filter(query, self._filters[filter_name], filter_name.value)

        if self._sort_by:  # TODO: Sorting isn't currently working as intended, because the main selected entity is BeatmapsetListing so it can only work on fields of that instead of fields of models like BeatmapsetSnapshot
            sort_fn = asc if self._sort_order == SortOrder.ASCENDING else desc
            query = query.order_by(sort_fn(getattr(BeatmapsetSnapshot, self._sort_by)))

        query = query.options(joinedload(BeatmapsetListing.beatmapset_snapshot))

        return query

    @staticmethod
    def _load_filter(filter_json: str) -> FilterDict:
        try:
            filter_ = json.loads(filter_json)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format for filter: {e}")

        if not isinstance(filter_, dict):
            raise ValueError(f"Invalid filter format: {filter_}. Must be a dict of fields and conditions")

        return filter_

    @staticmethod
    def _apply_filter(query: Select, filter_: FilterDict, model_class: ModelClass) -> Select:
        conditions = []

        for field, conditions_dict in filter_.items():
            for operator_str, value in conditions_dict.items():
                try:
                    operator = FilterOperator[operator_str.upper()]
                except KeyError:
                    raise ValueError(f"Invalid operator '{operator_str}' for field '{field}'")

                column = getattr(model_class.value, field, None)

                if column is None:
                    raise ValueError(f"Field '{field}' not found in model '{model_class}'")

                conditions.append(operator.value(column, value))

        if conditions:
            query = query.where(and_(*conditions))

        return query

    @property
    def search_query(self) -> str:
        return self._search_query

    @search_query.setter
    def search_query(self, search_query_: str):
        if not isinstance(search_query_, str):
            raise TypeError(f"Invalid search_query type: {type(search_query_)}. Must be str")

        self._search_query = search_query_

    @property
    def sort_by(self) -> str:
        return self._sort_by

    @sort_by.setter
    def sort_by(self, sort_by_: str):
        if not isinstance(sort_by_, str):
            raise TypeError(f"Invalid sort_by type: {type(sort_by_)}. Must be str")

        self._sort_by = sort_by_

    @property
    def sort_order(self) -> str:
        return self._sort_by

    @sort_order.setter
    def sort_order(self, sort_order_: SortOrder | Literal["asc", "desc"]):
        if isinstance(sort_order_, SortOrder):
            self._sort_order = sort_order_
        elif isinstance(sort_order_, str):
            if sort_order_ in (SortOrder.ASCENDING.value, SortOrder.DESCENDING.value):
                self._sort_order = SortOrder(sort_order_)
            else:
                raise ValueError(f"Invalid sort_order value as str: {sort_order_}. Must be '{SortOrder.ASCENDING.value}' or '{SortOrder.DESCENDING.value}'")
        else:
            raise TypeError(f"Invalid sort_order type: {type(sort_order_)}. Must be str or SortOrder")

    @property
    def mapper_filter(self) -> dict:
        return self._filters.get(FilterName.MAPPER)

    @mapper_filter.setter
    def mapper_filter(self, mapper_filter_json: str):
        if not isinstance(mapper_filter_json, str):
            raise TypeError(f"Invalid mapper_filter type: {type(mapper_filter_json)}. Must be str")

        self._filters[FilterName.MAPPER] = self._load_filter(mapper_filter_json)

    @property
    def beatmap_filter(self) -> dict:
        return self._filters.get(FilterName.BEATMAP)

    @beatmap_filter.setter
    def beatmap_filter(self, beatmap_filter_json: str):
        if not isinstance(beatmap_filter_json, str):
            raise TypeError(f"Invalid beatmap_filter type: {type(beatmap_filter_json)}. Must be str")

        self._filters[FilterName.BEATMAP] = self._load_filter(beatmap_filter_json)

    @property
    def beatmapset_filter(self) -> dict:
        return self._filters.get(FilterName.BEATMAPSET)

    @beatmapset_filter.setter
    def beatmapset_filter(self, beatmapset_filter_json: str):
        if not isinstance(beatmapset_filter_json, str):
            raise TypeError(f"Invalid beatmapset_filter type: {type(beatmapset_filter_json)}. Must be str")

        self._filters[FilterName.BEATMAPSET] = self._load_filter(beatmapset_filter_json)

    @property
    def request_filter(self) -> dict:
        return self._filters.get(FilterName.REQUEST)

    @request_filter.setter
    def request_filter(self, request_filter_json: str):
        if not isinstance(request_filter_json, str):
            raise TypeError(f"Invalid request_filter type: {type(request_filter_json)}. Must be str")

        self._filters[FilterName.REQUEST] = self._load_filter(request_filter_json)

    @property
    def queue_id(self) -> int:
        return self._queue_id

    @queue_id.setter
    def queue_id(self, queue_id_: int):
        if not isinstance(queue_id_, int):
            raise TypeError(f"Invalid queue_id type: {type(queue_id_)}. Must be int")

        self._queue_id = queue_id_
