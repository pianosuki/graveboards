from sqlalchemy.sql import select, delete
from sqlalchemy.orm.session import Session

from app.database.models import *
from app.database.schemas import *
from .decorators import session_manager


class _D:
    @staticmethod
    def _delete_instance(model_class: ModelClass, session: Session, **kwargs) -> bool:
        select_stmt = select(model_class.value).filter_by(**kwargs).limit(1)

        instance = session.scalar(select_stmt)

        if instance is None:
            return False

        session.delete(instance)
        session.commit()

        return True

    @staticmethod
    def _delete_instances(model_class: ModelClass, session: Session, **kwargs) -> int:
        delete_stmt = delete(model_class.value).filter_by(**kwargs)

        result = session.execute(delete_stmt)

        session.commit()

        return result.rowcount


class D(_D):
    @session_manager
    def delete_user(self, session: Session = None, **kwargs) -> bool:
        return self._delete_instance(ModelClass.USER, session, **kwargs)

    @session_manager
    def delete_users(self, session: Session = None, **kwargs) -> int:
        return self._delete_instances(ModelClass.USER, session, **kwargs)

    @session_manager
    def delete_role(self, session: Session = None, **kwargs) -> bool:
        return self._delete_instance(ModelClass.ROLE, session, **kwargs)

    @session_manager
    def delete_roles(self, session: Session = None, **kwargs) -> int:
        return self._delete_instances(ModelClass.ROLE, session, **kwargs)

    @session_manager
    def delete_mapper(self, session: Session = None, **kwargs) -> bool:
        return self._delete_instance(ModelClass.MAPPER, session, **kwargs)

    @session_manager
    def delete_mappers(self, session: Session = None, **kwargs) -> int:
        return self._delete_instances(ModelClass.MAPPER, session, **kwargs)

    @session_manager
    def delete_api_key(self, session: Session = None, **kwargs) -> bool:
        return self._delete_instance(ModelClass.API_KEY, session, **kwargs)

    @session_manager
    def delete_api_keys(self, session: Session = None, **kwargs) -> int:
        return self._delete_instances(ModelClass.API_KEY, session, **kwargs)

    @session_manager
    def delete_oauth_token(self, session: Session = None, **kwargs) -> bool:
        return self._delete_instance(ModelClass.OAUTH_TOKEN, session, **kwargs)

    @session_manager
    def delete_oauth_tokens(self, session: Session = None, **kwargs) -> int:
        return self._delete_instances(ModelClass.OAUTH_TOKEN, session, **kwargs)

    @session_manager
    def delete_score_fetcher_task(self, session: Session = None, **kwargs) -> bool:
        return self._delete_instance(ModelClass.SCORE_FETCHER_TASK, session, **kwargs)

    @session_manager
    def delete_score_fetcher_tasks(self, session: Session = None, **kwargs) -> int:
        return self._delete_instances(ModelClass.SCORE_FETCHER_TASK, session, **kwargs)

    @session_manager
    def delete_mapper_info_fetcher_task(self, session: Session = None, **kwargs) -> bool:
        return self._delete_instance(ModelClass.MAPPER_INFO_FETCHER_TASK, session, **kwargs)

    @session_manager
    def delete_mapper_info_fetcher_tasks(self, session: Session = None, **kwargs) -> int:
        return self._delete_instances(ModelClass.MAPPER_INFO_FETCHER_TASK, session, **kwargs)

    @session_manager
    def delete_beatmap(self, session: Session = None, **kwargs) -> bool:
        return self._delete_instance(ModelClass.BEATMAP, session, **kwargs)

    @session_manager
    def delete_beatmaps(self, session: Session = None, **kwargs) -> int:
        return self._delete_instances(ModelClass.BEATMAP, session, **kwargs)

    @session_manager
    def delete_beatmap_snapshot(self, session: Session = None, **kwargs) -> bool:
        return self._delete_instance(ModelClass.BEATMAP_SNAPSHOT, session, **kwargs)

    @session_manager
    def delete_beatmap_snapshots(self, session: Session = None, **kwargs) -> int:
        return self._delete_instances(ModelClass.BEATMAP_SNAPSHOT, session, **kwargs)

    @session_manager
    def delete_beatmapset(self, session: Session = None, **kwargs) -> bool:
        return self._delete_instance(ModelClass.BEATMAPSET, session, **kwargs)

    @session_manager
    def delete_beatmapsets(self, session: Session = None, **kwargs) -> int:
        return self._delete_instances(ModelClass.BEATMAPSET, session, **kwargs)

    @session_manager
    def delete_beatmapset_snapshot(self, session: Session = None, **kwargs) -> bool:
        return self._delete_instance(ModelClass.BEATMAPSET_SNAPSHOT, session, **kwargs)

    @session_manager
    def delete_beatmapset_snapshots(self, session: Session = None, **kwargs) -> int:
        return self._delete_instances(ModelClass.BEATMAPSET_SNAPSHOT, session, **kwargs)

    @session_manager
    def delete_beatmapset_listing(self, session: Session = None, **kwargs) -> bool:
        return self._delete_instance(ModelClass.BEATMAPSET_LISTING, session, **kwargs)

    @session_manager
    def delete_beatmapset_listings(self, session: Session = None, **kwargs) -> int:
        return self._delete_instances(ModelClass.BEATMAPSET_LISTING, session, **kwargs)

    @session_manager
    def delete_leaderboard(self, session: Session = None, **kwargs) -> bool:
        return self._delete_instance(ModelClass.LEADERBOARD, session, **kwargs)

    @session_manager
    def delete_leaderboards(self, session: Session = None, **kwargs) -> int:
        return self._delete_instances(ModelClass.LEADERBOARD, session, **kwargs)

    @session_manager
    def delete_score(self, session: Session = None, **kwargs) -> bool:
        return self._delete_instance(ModelClass.SCORE, session, **kwargs)

    @session_manager
    def delete_scores(self, session: Session = None, **kwargs) -> int:
        return self._delete_instances(ModelClass.SCORE, session, **kwargs)

    @session_manager
    def delete_queue(self, session: Session = None, **kwargs) -> bool:
        return self._delete_instance(ModelClass.QUEUE, session, **kwargs)

    @session_manager
    def delete_queues(self, session: Session = None, **kwargs) -> int:
        return self._delete_instances(ModelClass.QUEUE, session, **kwargs)

    @session_manager
    def delete_request(self, session: Session = None, **kwargs) -> bool:
        return self._delete_instance(ModelClass.REQUEST, session, **kwargs)

    @session_manager
    def delete_requests(self, session: Session = None, **kwargs) -> int:
        return self._delete_instances(ModelClass.REQUEST, session, **kwargs)
