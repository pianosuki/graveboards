from sqlalchemy.sql import select, desc
from sqlalchemy.orm.session import Session

from app.database.models import *
from app.database.schemas import *
from .decorators import session_manager


class _R:
    @staticmethod
    def _get_instance(
            model_class: ModelClass,
            session: Session,
            _reversed: bool = False,
            **kwargs
    ) -> BaseType:
        select_stmt = select(model_class.value).filter_by(**kwargs)

        if _reversed:
            primary_key_column = model_class.value.__mapper__.primary_key[0]
            select_stmt = select_stmt.order_by(desc(primary_key_column))

        return session.scalar(select_stmt)

    @staticmethod
    def _get_instances(
            model_class: ModelClass,
            session: Session,
            _limit: int = None,
            _offset: int = 0,
            _reversed: bool = False,
            **kwargs
    ) -> list[BaseType]:
        select_stmt = select(model_class.value).filter_by(**kwargs)

        if _reversed:
            primary_key_column = model_class.value.__mapper__.primary_key[0]
            select_stmt = select_stmt.order_by(desc(primary_key_column))

        select_stmt = select_stmt.limit(_limit).offset(_offset)

        return list(session.scalars(select_stmt).all())


class R(_R):
    @session_manager
    def get_user(self, session: Session = None, **kwargs) -> User | None:
        return self._get_instance(ModelClass.USER, session, **kwargs)

    @session_manager
    def get_users(self, session: Session = None, **kwargs) -> list[User]:
        return self._get_instances(ModelClass.USER, session, **kwargs)

    @session_manager
    def get_role(self, session: Session = None, **kwargs) -> Role | None:
        return self._get_instance(ModelClass.ROLE, session, **kwargs)

    @session_manager
    def get_roles(self, session: Session = None, **kwargs) -> list[Role]:
        return self._get_instances(ModelClass.ROLE, session, **kwargs)

    @session_manager
    def get_profile(self, session: Session = None, **kwargs) -> Profile | None:
        return self._get_instance(ModelClass.PROFILE, session, **kwargs)

    @session_manager
    def get_profiles(self, session: Session = None, **kwargs) -> list[Profile]:
        return self._get_instances(ModelClass.PROFILE, session, **kwargs)

    @session_manager
    def get_api_key(self, session: Session = None, **kwargs) -> ApiKey | None:
        return self._get_instance(ModelClass.API_KEY, session, **kwargs)

    @session_manager
    def get_api_keys(self, session: Session = None, **kwargs) -> list[ApiKey]:
        return self._get_instances(ModelClass.API_KEY, session, **kwargs)

    @session_manager
    def get_oauth_token(self, session: Session = None, **kwargs) -> OauthToken | None:
        return self._get_instance(ModelClass.OAUTH_TOKEN, session, **kwargs)

    @session_manager
    def get_oauth_tokens(self, session: Session = None, **kwargs) -> list[OauthToken]:
        return self._get_instances(ModelClass.OAUTH_TOKEN, session, **kwargs)

    @session_manager
    def get_score_fetcher_task(self, session: Session = None, **kwargs) -> ScoreFetcherTask | None:
        return self._get_instance(ModelClass.SCORE_FETCHER_TASK, session, **kwargs)

    @session_manager
    def get_score_fetcher_tasks(self, session: Session = None, **kwargs) -> list[ScoreFetcherTask]:
        return self._get_instances(ModelClass.SCORE_FETCHER_TASK, session, **kwargs)

    @session_manager
    def get_profile_fetcher_task(self, session: Session = None, **kwargs) -> ProfileFetcherTask | None:
        return self._get_instance(ModelClass.PROFILE_FETCHER_TASK, session, **kwargs)

    @session_manager
    def get_profile_fetcher_tasks(self, session: Session = None, **kwargs) -> list[ProfileFetcherTask]:
        return self._get_instances(ModelClass.PROFILE_FETCHER_TASK, session, **kwargs)

    @session_manager
    def get_beatmap(self, session: Session = None, **kwargs) -> Beatmap | None:
        return self._get_instance(ModelClass.BEATMAP, session, **kwargs)

    @session_manager
    def get_beatmaps(self, session: Session = None, **kwargs) -> list[Beatmap]:
        return self._get_instances(ModelClass.BEATMAP, session, **kwargs)

    @session_manager
    def get_beatmap_snapshot(self, session: Session = None, **kwargs) -> BeatmapSnapshot | None:
        return self._get_instance(ModelClass.BEATMAP_SNAPSHOT, session, **kwargs)

    @session_manager
    def get_beatmap_snapshots(self, session: Session = None, **kwargs) -> list[BeatmapSnapshot]:
        return self._get_instances(ModelClass.BEATMAP_SNAPSHOT, session, **kwargs)

    @session_manager
    def get_beatmapset(self, session: Session = None, **kwargs) -> Beatmapset | None:
        return self._get_instance(ModelClass.BEATMAPSET, session, **kwargs)

    @session_manager
    def get_beatmapsets(self, session: Session = None, **kwargs) -> list[Beatmapset]:
        return self._get_instances(ModelClass.BEATMAPSET, session, **kwargs)

    @session_manager
    def get_beatmapset_snapshot(self, session: Session = None, **kwargs) -> BeatmapsetSnapshot | None:
        return self._get_instance(ModelClass.BEATMAPSET_SNAPSHOT, session, **kwargs)

    @session_manager
    def get_beatmapset_snapshots(self, session: Session = None, **kwargs) -> list[BeatmapsetSnapshot]:
        return self._get_instances(ModelClass.BEATMAPSET_SNAPSHOT, session, **kwargs)

    @session_manager
    def get_beatmapset_listing(self, session: Session = None, **kwargs) -> BeatmapsetListing | None:
        return self._get_instance(ModelClass.BEATMAPSET_LISTING, session, **kwargs)

    @session_manager
    def get_beatmapset_listings(self, session: Session = None, **kwargs) -> list[BeatmapsetListing]:
        return self._get_instances(ModelClass.BEATMAPSET_LISTING, session, **kwargs)

    @session_manager
    def get_leaderboard(self, session: Session = None, **kwargs) -> Leaderboard | None:
        return self._get_instance(ModelClass.LEADERBOARD, session, **kwargs)

    @session_manager
    def get_leaderboards(self, session: Session = None, **kwargs) -> list[Leaderboard]:
        return self._get_instances(ModelClass.LEADERBOARD, session, **kwargs)

    @session_manager
    def get_score(self, session: Session = None, **kwargs) -> Score | None:
        return self._get_instance(ModelClass.SCORE, session, **kwargs)

    @session_manager
    def get_scores(self, session: Session = None, **kwargs) -> list[Score]:
        return self._get_instances(ModelClass.SCORE, session, **kwargs)

    @session_manager
    def get_queue(self, session: Session = None, **kwargs) -> Queue | None:
        return self._get_instance(ModelClass.QUEUE, session, **kwargs)

    @session_manager
    def get_queues(self, session: Session = None, **kwargs) -> list[Queue]:
        return self._get_instances(ModelClass.QUEUE, session, **kwargs)

    @session_manager
    def get_request(self, session: Session = None, **kwargs) -> Request | None:
        return self._get_instance(ModelClass.REQUEST, session, **kwargs)

    @session_manager
    def get_requests(self, session: Session = None, **kwargs) -> list[Request]:
        return self._get_instances(ModelClass.REQUEST, session, **kwargs)

    @session_manager
    def get_tag(self, session: Session = None, **kwargs) -> Tag | None:
        return self._get_instance(ModelClass.TAG, session, **kwargs)

    @session_manager
    def get_tags(self, session: Session = None, **kwargs) -> list[Tag]:
        return self._get_instances(ModelClass.TAG, session, **kwargs)
