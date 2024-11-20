from sqlalchemy.orm.session import Session

from app.database.models import *
from app.database.schemas import *
from .decorators import session_manager


class _U:
    @staticmethod
    def _update_instance(model_class: ModelClass, session: Session, primary_key: int, **kwargs) -> BaseType:
        instance = session.get(model_class.value, primary_key)

        if instance is None:
            raise ValueError(f"There is no {model_class.value.__name__} with the primary key '{primary_key}'")

        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
            else:
                raise ValueError(f"{model_class.value.__name__} has no attribute '{key}'")

        session.commit()
        session.refresh(instance)

        return instance


class U(_U):
    @session_manager
    def update_user(self, primary_key: int, session: Session = None, **kwargs) -> User:
        return self._update_instance(ModelClass.USER, session, primary_key, **kwargs)

    @session_manager
    def update_role(self, primary_key: int, session: Session = None, **kwargs) -> Role:
        return self._update_instance(ModelClass.ROLE, session, primary_key, **kwargs)

    @session_manager
    def update_profile(self, primary_key: int, session: Session = None, **kwargs) -> Profile:
        return self._update_instance(ModelClass.PROFILE, session, primary_key, **kwargs)

    @session_manager
    def update_api_key(self, primary_key: int, session: Session = None, **kwargs) -> ApiKey:
        return self._update_instance(ModelClass.API_KEY, session, primary_key, **kwargs)

    @session_manager
    def update_oauth_token(self, primary_key: int, session: Session = None, **kwargs) -> OauthToken:
        return self._update_instance(ModelClass.OAUTH_TOKEN, session, primary_key, **kwargs)

    @session_manager
    def update_score_fetcher_task(self, primary_key: int, session: Session = None, **kwargs) -> ScoreFetcherTask:
        return self._update_instance(ModelClass.SCORE_FETCHER_TASK, session, primary_key, **kwargs)

    @session_manager
    def update_profile_fetcher_task(self, primary_key: int, session: Session = None, **kwargs) -> ProfileFetcherTask:
        return self._update_instance(ModelClass.PROFILE_FETCHER_TASK, session, primary_key, **kwargs)

    @session_manager
    def update_beatmap(self, primary_key: int, session: Session = None, **kwargs) -> Beatmap:
        return self._update_instance(ModelClass.BEATMAP, session, primary_key, **kwargs)

    @session_manager
    def update_beatmap_snapshot(self, primary_key: int, session: Session = None, **kwargs) -> BeatmapSnapshot:
        return self._update_instance(ModelClass.BEATMAP_SNAPSHOT, session, primary_key, **kwargs)

    @session_manager
    def update_beatmapset(self, primary_key: int, session: Session = None, **kwargs) -> Beatmapset:
        return self._update_instance(ModelClass.BEATMAPSET, session, primary_key, **kwargs)

    @session_manager
    def update_beatmapset_snapshot(self, primary_key: int, session: Session = None, **kwargs) -> BeatmapsetSnapshot:
        return self._update_instance(ModelClass.BEATMAPSET_SNAPSHOT, session, primary_key, **kwargs)

    @session_manager
    def update_beatmapset_listing(self, primary_key: int, session: Session = None, **kwargs) -> BeatmapsetListing:
        return self._update_instance(ModelClass.BEATMAPSET_LISTING, session, primary_key, **kwargs)

    @session_manager
    def update_leaderboard(self, primary_key: int, session: Session = None, **kwargs) -> Leaderboard:
        return self._update_instance(ModelClass.LEADERBOARD, session, primary_key, **kwargs)

    @session_manager
    def update_score(self, primary_key: int, session: Session = None, **kwargs) -> Score:
        return self._update_instance(ModelClass.SCORE, session, primary_key, **kwargs)

    @session_manager
    def update_queue(self, primary_key: int, session: Session = None, **kwargs) -> Queue:
        return self._update_instance(ModelClass.QUEUE, session, primary_key, **kwargs)

    @session_manager
    def update_request(self, primary_key: int, session: Session = None, **kwargs) -> Request:
        return self._update_instance(ModelClass.REQUEST, session, primary_key, **kwargs)

    @session_manager
    def update_tag(self, primary_key: int, session: Session = None, **kwargs) -> Tag:
        return self._update_instance(ModelClass.TAG, session, primary_key, **kwargs)
