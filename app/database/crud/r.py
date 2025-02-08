from typing import Iterable, Literal

from sqlalchemy.sql import select, desc
from sqlalchemy.sql.selectable import Select
from sqlalchemy.orm.strategy_options import selectinload, joinedload, noload, defer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import *
from app.utils import clamp
from .decorators import session_manager

LoadingStrategy = Literal["joinedload", "selectinload"]
QUERY_MIN_LIMIT = 1
QUERY_MAX_LIMIT = 100
QUERY_DEFAULT_LIMIT = 50


class _R:
    @staticmethod
    async def _get_instance(
            model_class: ModelClass,
            session: AsyncSession,
            **kwargs
    ) -> BaseType:
        select_stmt = _R._construct_stmt(model_class, **kwargs)

        return await session.scalar(select_stmt)

    @staticmethod
    async def _get_instances(
            model_class: ModelClass,
            session: AsyncSession,
            _limit: int = QUERY_DEFAULT_LIMIT,
            _offset: int = 0,
            **kwargs
    ) -> list[BaseType]:
        select_stmt = _R._construct_stmt(model_class, **kwargs)
        select_stmt = select_stmt.limit(clamp(_limit, QUERY_MIN_LIMIT, QUERY_MAX_LIMIT)).offset(_offset)

        return list((await session.scalars(select_stmt)).all())

    @staticmethod
    def _construct_stmt(
            model_class: ModelClass,
            _reversed: bool = False,
            _eager_loads: dict[str, LoadingStrategy] = None,
            _auto_eager_loads: Iterable[str] = None,
            _exclude: Iterable[str] = None,
            _exclude_lazy: bool = False,
            **kwargs
    ) -> Select:
        if _eager_loads and _auto_eager_loads:
            raise ValueError("_eager_loads and _auto_eager_loads are mutually exclusive")

        select_stmt = select(model_class.value).filter_by(**kwargs)

        if _reversed:
            select_stmt = _R._apply_reversed(select_stmt, model_class)

        if _eager_loads:
            select_stmt = _R._apply_eager_loads(select_stmt, model_class, _eager_loads)
        elif _auto_eager_loads:
            select_stmt = _R._apply_auto_eager_loads(select_stmt, model_class, _auto_eager_loads)

        if _exclude:
            select_stmt = _R._apply_exclude(select_stmt, model_class, _exclude)

        if _exclude_lazy:
            select_stmt = _R._apply_exclude_lazy(select_stmt, model_class)

        return select_stmt

    @staticmethod
    def _apply_reversed(select_stmt: Select, model_class: ModelClass) -> Select:
        return select_stmt.order_by(desc(model_class.mapper.primary_key[0]))

    @staticmethod
    def _apply_eager_loads(select_stmt: Select, model_class: ModelClass, eager_loads: dict[str, LoadingStrategy]) -> Select:
        load_options = []

        for relationship_name, strategy_name in eager_loads.items():
            if relationship_name in model_class.mapper.relationships:
                relationship = model_class.mapper.attrs[relationship_name]

                if strategy_name == "joinedload":
                    load_options.append(joinedload(relationship))
                elif strategy_name == "selectinload":
                    load_options.append(selectinload(relationship))
                else:
                    raise ValueError(f"Unsupported loading strategy: {strategy_name}")
            else:
                raise ValueError(f"{relationship_name} is not a valid relationship in {model_class.value}")

        return select_stmt.options(*load_options)

    @staticmethod
    def _apply_auto_eager_loads(select_stmt: Select, model_class: ModelClass, relationships: Iterable[str]) -> Select:
        load_options = []

        for relationship_name in relationships:
            if relationship_name in model_class.mapper.relationships:
                relationship = model_class.mapper.attrs[relationship_name]
                is_collection = model_class.mapper.relationships[relationship_name].uselist

                if is_collection:
                    load_options.append(selectinload(relationship))
                else:
                    load_options.append(joinedload(relationship))
            else:
                raise ValueError(f"{relationship_name} is not a valid relationship in {model_class.value}")

        return select_stmt.options(*load_options)

    @staticmethod
    def _apply_exclude(select_stmt: Select, model_class: ModelClass, exclude: Iterable[str]) -> Select:
        load_options = []

        for attr_name in exclude:
            if attr_name in model_class.mapper.columns:
                column = model_class.mapper.attrs[attr_name]
                load_options.append(defer(column))
            elif attr_name in model_class.mapper.relationships:
                relationship = model_class.mapper.attrs[attr_name]
                load_options.append(noload(relationship))
            else:
                raise ValueError(f"{attr_name} is not a valid column or relationship in {model_class.value}")

        return select_stmt.options(*load_options)


    @staticmethod
    def _apply_exclude_lazy(select_stmt: Select, model_class: ModelClass) -> Select:
        noload_relationships = [
            noload(relationship)
            for relationship in model_class.mapper.relationships
            if relationship.lazy is True or relationship.lazy in {"select", "dynamic", "raise_on_sql"}
        ]

        return select_stmt.options(*noload_relationships)


class R(_R):
    @session_manager
    async def get_user(self, session: AsyncSession = None, **kwargs) -> User | None:
        return await self._get_instance(ModelClass.USER, session, **kwargs)

    @session_manager
    async def get_users(self, session: AsyncSession = None, **kwargs) -> list[User]:
        return await self._get_instances(ModelClass.USER, session, **kwargs)

    @session_manager
    async def get_role(self, session: AsyncSession = None, **kwargs) -> Role | None:
        return await self._get_instance(ModelClass.ROLE, session, **kwargs)

    @session_manager
    async def get_roles(self, session: AsyncSession = None, **kwargs) -> list[Role]:
        return await self._get_instances(ModelClass.ROLE, session, **kwargs)

    @session_manager
    async def get_profile(self, session: AsyncSession = None, **kwargs) -> Profile | None:
        return await self._get_instance(ModelClass.PROFILE, session, **kwargs)

    @session_manager
    async def get_profiles(self, session: AsyncSession = None, **kwargs) -> list[Profile]:
        return await self._get_instances(ModelClass.PROFILE, session, **kwargs)

    @session_manager
    async def get_api_key(self, session: AsyncSession = None, **kwargs) -> ApiKey | None:
        return await self._get_instance(ModelClass.API_KEY, session, **kwargs)

    @session_manager
    async def get_api_keys(self, session: AsyncSession = None, **kwargs) -> list[ApiKey]:
        return await self._get_instances(ModelClass.API_KEY, session, **kwargs)

    @session_manager
    async def get_oauth_token(self, session: AsyncSession = None, **kwargs) -> OAuthToken | None:
        return await self._get_instance(ModelClass.OAUTH_TOKEN, session, **kwargs)

    @session_manager
    async def get_oauth_tokens(self, session: AsyncSession = None, **kwargs) -> list[OAuthToken]:
        return await self._get_instances(ModelClass.OAUTH_TOKEN, session, **kwargs)

    @session_manager
    async def get_jwt(self, session: AsyncSession = None, **kwargs) -> JWT | None:
        return await self._get_instance(ModelClass.JWT, session, **kwargs)

    @session_manager
    async def get_jwts(self, session: AsyncSession = None, **kwargs) -> list[JWT]:
        return await self._get_instances(ModelClass.JWT, session, **kwargs)

    @session_manager
    async def get_score_fetcher_task(self, session: AsyncSession = None, **kwargs) -> ScoreFetcherTask | None:
        return await self._get_instance(ModelClass.SCORE_FETCHER_TASK, session, **kwargs)

    @session_manager
    async def get_score_fetcher_tasks(self, session: AsyncSession = None, **kwargs) -> list[ScoreFetcherTask]:
        return await self._get_instances(ModelClass.SCORE_FETCHER_TASK, session, **kwargs)

    @session_manager
    async def get_profile_fetcher_task(self, session: AsyncSession = None, **kwargs) -> ProfileFetcherTask | None:
        return await self._get_instance(ModelClass.PROFILE_FETCHER_TASK, session, **kwargs)

    @session_manager
    async def get_profile_fetcher_tasks(self, session: AsyncSession = None, **kwargs) -> list[ProfileFetcherTask]:
        return await self._get_instances(ModelClass.PROFILE_FETCHER_TASK, session, **kwargs)

    @session_manager
    async def get_beatmap(self, session: AsyncSession = None, **kwargs) -> Beatmap | None:
        return await self._get_instance(ModelClass.BEATMAP, session, **kwargs)

    @session_manager
    async def get_beatmaps(self, session: AsyncSession = None, **kwargs) -> list[Beatmap]:
        return await self._get_instances(ModelClass.BEATMAP, session, **kwargs)

    @session_manager
    async def get_beatmap_snapshot(self, session: AsyncSession = None, **kwargs) -> BeatmapSnapshot | None:
        return await self._get_instance(ModelClass.BEATMAP_SNAPSHOT, session, **kwargs)

    @session_manager
    async def get_beatmap_snapshots(self, session: AsyncSession = None, **kwargs) -> list[BeatmapSnapshot]:
        return await self._get_instances(ModelClass.BEATMAP_SNAPSHOT, session, **kwargs)

    @session_manager
    async def get_beatmapset(self, session: AsyncSession = None, **kwargs) -> Beatmapset | None:
        return await self._get_instance(ModelClass.BEATMAPSET, session, **kwargs)

    @session_manager
    async def get_beatmapsets(self, session: AsyncSession = None, **kwargs) -> list[Beatmapset]:
        return await self._get_instances(ModelClass.BEATMAPSET, session, **kwargs)

    @session_manager
    async def get_beatmapset_snapshot(self, session: AsyncSession = None, **kwargs) -> BeatmapsetSnapshot | None:
        return await self._get_instance(ModelClass.BEATMAPSET_SNAPSHOT, session, **kwargs)

    @session_manager
    async def get_beatmapset_snapshots(self, session: AsyncSession = None, **kwargs) -> list[BeatmapsetSnapshot]:
        return await self._get_instances(ModelClass.BEATMAPSET_SNAPSHOT, session, **kwargs)

    @session_manager
    async def get_beatmapset_listing(self, session: AsyncSession = None, **kwargs) -> BeatmapsetListing | None:
        return await self._get_instance(ModelClass.BEATMAPSET_LISTING, session, **kwargs)

    @session_manager
    async def get_beatmapset_listings(self, session: AsyncSession = None, **kwargs) -> list[BeatmapsetListing]:
        return await self._get_instances(ModelClass.BEATMAPSET_LISTING, session, **kwargs)

    @session_manager
    async def get_leaderboard(self, session: AsyncSession = None, **kwargs) -> Leaderboard | None:
        return await self._get_instance(ModelClass.LEADERBOARD, session, **kwargs)

    @session_manager
    async def get_leaderboards(self, session: AsyncSession = None, **kwargs) -> list[Leaderboard]:
        return await self._get_instances(ModelClass.LEADERBOARD, session, **kwargs)

    @session_manager
    async def get_score(self, session: AsyncSession = None, **kwargs) -> Score | None:
        return await self._get_instance(ModelClass.SCORE, session, **kwargs)

    @session_manager
    async def get_scores(self, session: AsyncSession = None, **kwargs) -> list[Score]:
        return await self._get_instances(ModelClass.SCORE, session, **kwargs)

    @session_manager
    async def get_queue(self, session: AsyncSession = None, **kwargs) -> Queue | None:
        return await self._get_instance(ModelClass.QUEUE, session, **kwargs)

    @session_manager
    async def get_queues(self, session: AsyncSession = None, **kwargs) -> list[Queue]:
        return await self._get_instances(ModelClass.QUEUE, session, **kwargs)

    @session_manager
    async def get_request(self, session: AsyncSession = None, **kwargs) -> Request | None:
        return await self._get_instance(ModelClass.REQUEST, session, **kwargs)

    @session_manager
    async def get_requests(self, session: AsyncSession = None, **kwargs) -> list[Request]:
        return await self._get_instances(ModelClass.REQUEST, session, **kwargs)

    @session_manager
    async def get_tag(self, session: AsyncSession = None, **kwargs) -> Tag | None:
        return await self._get_instance(ModelClass.TAG, session, **kwargs)

    @session_manager
    async def get_tags(self, session: AsyncSession = None, **kwargs) -> list[Tag]:
        return await self._get_instances(ModelClass.TAG, session, **kwargs)
