import json
from typing import Literal, Generator

from sqlalchemy.sql import select, and_
from sqlalchemy.sql.selectable import Select
from sqlalchemy.sql.elements import ColumnClause, BinaryExpression
from sqlalchemy.sql.expression import CTE
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.session import Session
from sqlalchemy.dialects import postgresql

from app.database.models import Profile, BeatmapSnapshot, BeatmapsetSnapshot, BeatmapsetListing, Queue, Request, ModelClass
from app.database.utils import validate_column_value, get_filter_condition
from app.database.ctes.hashable_cte import HashableCTE
from app.database.ctes.bm_ss_sorting import bm_ss_sorting_cte_factory
from app.database.ctes.search_filter import search_filter_cte_factory
from app.database.ctes.bm_ss_filtering import bm_ss_filtering_cte_factory
from app.database.ctes.profile_sorting import profile_sorting_cte_factory
from app.database.ctes.profile_filtering import profile_filtering_cte_factory
from app.database.ctes.request_sorting import request_sorting_cte_factory
from app.database.ctes.request_filtering import request_filtering_cte_factory
from app.exceptions import TypeValidationError
from .enums import FilterName, SortOrder, FilterOperator, AdvancedFilterField, SortingField

PaginatedResultsGenerator = Generator[list[BeatmapsetListing], Session, None]
FilterDict = dict[str, dict]


class SearchEngine:
    def __init__(self):
        self._search_query: str = ""
        self._sorting: list[SortingField] = []
        self._sort_orders: list[SortOrder] = []
        self._filters: dict[FilterName, FilterDict] = {filter_name: {} for filter_name in FilterName}
        self._queue_id: int | None = None
        self._limit: int = 50
        self._offset: int = 0
        self._requests_only: bool = False

        self.query: Select | None = None

    def search(
        self,
        search_query: str = None,
        sorting: list[str] = None,
        sort_orders: list[str] = None,
        mapper_filter: str = None,
        beatmap_filter: str = None,
        beatmapset_filter: str = None,
        request_filter: str = None,
        queue_id: int = None,
        limit: int = None,
        offset: int = None,
        requests_only: bool = False
    ) -> PaginatedResultsGenerator:
        if search_query:
            self.search_query = search_query
        if sorting:
            self.sorting = sorting
        if sort_orders:
            self.sort_orders = sort_orders
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
        if requests_only:
            self._requests_only = requests_only

        self.compose_query()

        return self.results_generator()

    def results_generator(self) -> PaginatedResultsGenerator:
        while True:
            page_query = self.query.limit(self._limit).offset(self._offset)

            session: Session = yield
            results = session.execute(page_query).scalars().all() if not self._requests_only else session.execute(page_query).all()

            if not results:
                break

            yield results

            self._offset += self._limit

    def compose_query(self):
        if not self._requests_only:
            self.query = (
                select(BeatmapsetListing)
                .join(
                    BeatmapsetSnapshot,
                    BeatmapsetSnapshot.id == BeatmapsetListing.beatmapset_snapshot_id
                )
            )
        else:
            self.query = (
                select(BeatmapsetListing, Request)
                .join(
                    BeatmapsetSnapshot,
                    BeatmapsetSnapshot.id == BeatmapsetListing.beatmapset_snapshot_id
                )
                .join(
                    Request,
                    Request.beatmapset_id == BeatmapsetSnapshot.beatmapset_id
                )
            )

        for idx, sorting_field in enumerate(self.sorting):
            try:
                sort_order = self.sort_orders[idx]
            except IndexError:
                sort_order = SortOrder.ASCENDING

            self._apply_sorting(sorting_field, sort_order)

        if self.queue_id:
            request_cte = (
                select(Request.id, Request.beatmapset_id)
                .join(Queue, Queue.id == Request.queue_id)
                .where(Queue.id == self.queue_id)
                .cte("request_cte")
            )

            if not self._requests_only:
                self.query = self.query.join(request_cte, request_cte.c.beatmapset_id == BeatmapsetSnapshot.beatmapset_id)
            else:
                self.query = self.query.join(request_cte, request_cte.c.id == Request.id)

        if self.search_query:
            cte = search_filter_cte_factory(self.search_query)

            self.query = self.query.join(cte, cte.c.beatmapset_snapshot_id == BeatmapsetSnapshot.id)

        for filter_name, filter_ in self._filters.items():
            if not filter_:
                continue

            self._apply_filter(self._filters[filter_name], filter_name.value)

    @staticmethod
    def _load_sorting(sorting: list[str]) -> list[SortingField]:
        sorting_ = []

        for sorting_target in sorting:
            try:
                sorting_field = getattr(SortingField, sorting_target.replace(".", "__").upper())
                sorting_.append(sorting_field)
            except KeyError:
                raise ValueError(f"Invalid sorting field: '{sorting_target}'")

        return sorting_

    def _apply_sorting(self, sorting_field: SortingField, sort_order: SortOrder):
        def apply_cte(rows_ranked: bool = True):
            self.query = (
                self.query
                .join(cte, cte.c.beatmapset_snapshot_id == BeatmapsetSnapshot.id)
                .order_by(sort_order.sort_func(cte.c.target))
            )

            if rows_ranked:
                self.query = self.query.where(cte.c.rank == 1)

        match sorting_field.model_class:
            case ModelClass.PROFILE:
                cte = profile_sorting_cte_factory(sorting_field.value, sort_order)
                apply_cte()
            case ModelClass.BEATMAP_SNAPSHOT:
                cte = bm_ss_sorting_cte_factory(sorting_field.value, sort_order)
                apply_cte()
            case ModelClass.BEATMAPSET_SNAPSHOT:
                if isinstance(sorting_field.value, InstrumentedAttribute):
                    self.query = self.query.order_by(sort_order.sort_func(sorting_field.value))
                elif isinstance(sorting_field.value, HashableCTE):
                    cte = sorting_field.value.cte
                    cte = cte.alias("sorting_" + cte.name)
                    apply_cte(rows_ranked=False)
            case ModelClass.REQUEST:
                cte = request_sorting_cte_factory(sorting_field.value, sort_order)
                apply_cte()

    @staticmethod
    def _load_filter(filter_json: str) -> FilterDict:
        try:
            filter_ = json.loads(filter_json)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format for filter: {e}")

        if not isinstance(filter_, dict):
            raise ValueError(f"Invalid filter format: {filter_}. Must be a dict of fields and conditions")

        return filter_

    def _apply_filter(self, filter_: FilterDict, model_class: ModelClass):
        def condition_generator(conditions_dict: dict, target: InstrumentedAttribute | ColumnClause, is_aggregated: bool = False) -> Generator[BinaryExpression, None, None]:
            if not isinstance(conditions_dict, dict):
                raise ValueError(f"Invalid conditions format for field '{field}': {conditions_dict}. Must be a dict of operators and values")

            for operator_str, value in conditions_dict.items():
                operator_str = operator_str.lower()

                try:
                    filter_operator = getattr(FilterOperator, operator_str.upper())
                except KeyError:
                    raise ValueError(f"Invalid operator '{operator_str}' for field '{field}' in condition {dict({operator_str: value})}")

                if column_is_column:  # TODO: Validate against hybrid too
                    try:
                        validate_column_value(column, value)
                    except TypeValidationError as e:
                        raise TypeError(f"Invalid value type for field '{field}' in condition {dict({operator_str: value})}: Expected {e.expected_types}, got {e.value_type.__name__}")
                    except ValueError as e:
                        raise e

                yield get_filter_condition(filter_operator, target, value, is_aggregated=is_aggregated)

        def apply_conditions(target: InstrumentedAttribute | ColumnClause, conditions_dict: dict):
            for condition in condition_generator(conditions_dict, target):
                conditions.append(condition)

        def apply_cte(cte: CTE, conditions_dict: dict):
            target = cte.columns["target"]
            apply_conditions(target, conditions_dict)

            self.query = self.query.join(cte, BeatmapsetSnapshot.id == cte.c.beatmapset_snapshot_id)

        def apply_simple_filter():
            if column.class_ is Profile:
                cte = profile_filtering_cte_factory(column)
                self.query = self.query.join(cte, cte.c.beatmapset_snapshot_id == BeatmapsetSnapshot.id)
                apply_conditions(cte.c.target, field_value)
            elif column.class_ is BeatmapSnapshot:
                aggregated_conditions = condition_generator(field_value, column, is_aggregated=True)
                cte = bm_ss_filtering_cte_factory(column, aggregated_conditions)
                self.query = self.query.join(cte, cte.c.beatmapset_snapshot_id == BeatmapsetSnapshot.id)
            elif column.class_ is Request:
                cte = request_filtering_cte_factory(column)
                self.query = self.query.join(cte, cte.c.beatmapset_snapshot_id == BeatmapsetSnapshot.id)
                apply_conditions(cte.c.target, field_value)
            else:
                apply_conditions(column, field_value)

        def apply_advanced_filter():
            advanced_filter_field = AdvancedFilterField[field.upper()]

            if isinstance(advanced_filter_field.value, dict):
                for func_str, conditions_dict in field_value.items():
                    func_str = func_str.lower()

                    try:
                        cte = advanced_filter_field.value[func_str]
                        cte = cte.alias("filtering_" + cte.name)
                    except KeyError:
                        raise ValueError(f"Unsupported function '{func_str}' for field '{field}'. Must be one of: {", ".join(advanced_filter_field.value.keys())}")

                    return apply_cte(cte, conditions_dict)
            elif isinstance(advanced_filter_field.value, CTE):
                cte = advanced_filter_field.value
                return apply_cte(cte, field_value)
            else:
                raise ValueError(f"Unknown error occurred while processing field '{field}'. Please let a developer know")

        conditions: list[BinaryExpression] = []

        for field, field_value in filter_.items():
            field = field.lower()
            column = getattr(model_class.value, field, None)

            column_is_column = isinstance(column, InstrumentedAttribute)
            column_is_hybrid = column is not None and field in model_class.value.__annotations__.keys() and field not in model_class.value.__mapper__.c.keys()
            needs_advanced_filtering = column_is_hybrid and field.upper() in AdvancedFilterField.__members__.keys()

            if not column_is_column and not column_is_hybrid:
                raise ValueError(f"Field '{field}' not applicable to '{model_class.value.__name__}'")

            if not needs_advanced_filtering:
                apply_simple_filter()
            else:
                apply_advanced_filter()

        if conditions:
            self.query = self.query.where(and_(*conditions))

    @property
    def search_query(self) -> str:
        return self._search_query

    @search_query.setter
    def search_query(self, search_query_: str):
        if not isinstance(search_query_, str):
            raise TypeError(f"Invalid search_query type: {type(search_query_).__name__}. Must be str")

        self._search_query = search_query_

    @property
    def sorting(self) -> list[SortingField]:
        return self._sorting

    @sorting.setter
    def sorting(self, sorting_: list[str]):
        if not isinstance(sorting_, list) or (isinstance(sorting_, list) and not all(isinstance(sorting_target, str) for sorting_target in sorting_)):
            raise TypeError(f"Invalid sorting type: {type(sorting_).__name__}. Must be a list of strings")

        self._sorting = self._load_sorting(sorting_)

    @property
    def sort_orders(self) -> list[SortOrder]:
        return self._sort_orders

    @sort_orders.setter
    def sort_orders(self, sort_orders_: list[SortOrder] | list[Literal["asc", "desc"]]):
        if all(isinstance(sort_order_, SortOrder) for sort_order_ in sort_orders_):
            self._sort_orders = sort_orders_
        elif all(isinstance(sort_order_, str) for sort_order_ in sort_orders_):
            if not all(sort_order_ in (SortOrder.ASCENDING.value, SortOrder.DESCENDING.value) for sort_order_ in sort_orders_):
                raise ValueError(f"sort_orders as str must only contain '{SortOrder.ASCENDING.value}' or '{SortOrder.DESCENDING.value}'")

            self._sort_orders = [SortOrder(sort_order_) for sort_order_ in sort_orders_]
        else:
            raise TypeError("sort_orders must either only contain SortOrder or only contain str")

    @property
    def mapper_filter(self) -> dict:
        return self._filters.get(FilterName.MAPPER)

    @mapper_filter.setter
    def mapper_filter(self, mapper_filter_json: str):
        if not isinstance(mapper_filter_json, str):
            raise TypeError(f"Invalid mapper_filter type: {type(mapper_filter_json).__name__}. Must be str")

        self._filters[FilterName.MAPPER] = self._load_filter(mapper_filter_json)

    @property
    def beatmap_filter(self) -> dict:
        return self._filters.get(FilterName.BEATMAP)

    @beatmap_filter.setter
    def beatmap_filter(self, beatmap_filter_json: str):
        if not isinstance(beatmap_filter_json, str):
            raise TypeError(f"Invalid beatmap_filter type: {type(beatmap_filter_json).__name__}. Must be str")

        self._filters[FilterName.BEATMAP] = self._load_filter(beatmap_filter_json)

    @property
    def beatmapset_filter(self) -> dict:
        return self._filters.get(FilterName.BEATMAPSET)

    @beatmapset_filter.setter
    def beatmapset_filter(self, beatmapset_filter_json: str):
        if not isinstance(beatmapset_filter_json, str):
            raise TypeError(f"Invalid beatmapset_filter type: {type(beatmapset_filter_json).__name__}. Must be str")

        self._filters[FilterName.BEATMAPSET] = self._load_filter(beatmapset_filter_json)

    @property
    def request_filter(self) -> dict:
        return self._filters.get(FilterName.REQUEST)

    @request_filter.setter
    def request_filter(self, request_filter_json: str):
        if not isinstance(request_filter_json, str):
            raise TypeError(f"Invalid request_filter type: {type(request_filter_json).__name__}. Must be str")

        self._filters[FilterName.REQUEST] = self._load_filter(request_filter_json)

    @property
    def queue_id(self) -> int:
        return self._queue_id

    @queue_id.setter
    def queue_id(self, queue_id_: int):
        if not isinstance(queue_id_, int):
            raise TypeError(f"Invalid queue_id type: {type(queue_id_).__name__}. Must be int")

        self._queue_id = queue_id_

    @property
    def compiled_query(self) -> str:
        if not self.query:
            raise ValueError("The query is empty")

        return str(self.query.compile(dialect=postgresql.dialect()))
