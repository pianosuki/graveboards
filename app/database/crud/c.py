from sqlalchemy.orm.session import Session

from app.database.models import *
from app.database.schemas import *
from .decorators import session_manager, ensure_required


class _C:
    @staticmethod
    @ensure_required
    def _add_instance(model_class: ModelClass, session: Session, **kwargs) -> BaseType:
        instance = model_class.value(**kwargs)

        session.add(instance)
        session.commit()
        session.refresh(instance)

        return instance


class C(_C):
    @session_manager
    def add_user(self, session: Session = None, **kwargs) -> User:
        return self._add_instance(ModelClass.USER, session, **kwargs)

    @session_manager
    def add_role(self, session: Session = None, **kwargs) -> Role:
        return self._add_instance(ModelClass.ROLE, session, **kwargs)

    @session_manager
    def add_profile(self, session: Session = None, **kwargs) -> Profile:
        return self._add_instance(ModelClass.PROFILE, session, **kwargs)

    @session_manager
    def add_api_key(self, session: Session = None, **kwargs) -> ApiKey:
        return self._add_instance(ModelClass.API_KEY, session, **kwargs)

    @session_manager
    def add_oauth_token(self, session: Session = None, **kwargs) -> OauthToken:
        return self._add_instance(ModelClass.OAUTH_TOKEN, session, **kwargs)

    @session_manager
    def add_score_fetcher_task(self, session: Session = None, **kwargs) -> ScoreFetcherTask:
        return self._add_instance(ModelClass.SCORE_FETCHER_TASK, session, **kwargs)

    @session_manager
    def add_profile_fetcher_task(self, session: Session = None, **kwargs) -> ProfileFetcherTask:
        return self._add_instance(ModelClass.PROFILE_FETCHER_TASK, session, **kwargs)

    @session_manager
    def add_beatmap(self, session: Session = None, **kwargs) -> Beatmap:
        return self._add_instance(ModelClass.BEATMAP, session, **kwargs)

    @session_manager
    def add_beatmap_snapshot(self, session: Session = None, **kwargs) -> BeatmapSnapshot:
        return self._add_instance(ModelClass.BEATMAP_SNAPSHOT, session, **kwargs)

    @session_manager
    def add_beatmapset(self, session: Session = None, **kwargs) -> Beatmapset:
        return self._add_instance(ModelClass.BEATMAPSET, session, **kwargs)

    @session_manager
    def add_beatmapset_snapshot(self, session: Session = None, **kwargs) -> BeatmapsetSnapshot:
        return self._add_instance(ModelClass.BEATMAPSET_SNAPSHOT, session, **kwargs)

    @session_manager
    def add_beatmapset_listing(self, session: Session = None, **kwargs) -> BeatmapsetListing:
        return self._add_instance(ModelClass.BEATMAPSET_LISTING, session, **kwargs)

    @session_manager
    def add_leaderboard(self, session: Session = None, **kwargs) -> Leaderboard:
        return self._add_instance(ModelClass.LEADERBOARD, session, **kwargs)

    @session_manager
    def add_score(self, session: Session = None, **kwargs) -> Score:
        return self._add_instance(ModelClass.SCORE, session, **kwargs)

    @session_manager
    def add_queue(self, session: Session = None, **kwargs) -> Queue:
        return self._add_instance(ModelClass.QUEUE, session, **kwargs)

    @session_manager
    def add_request(self, session: Session = None, **kwargs) -> Request:
        return self._add_instance(ModelClass.REQUEST, session, **kwargs)
