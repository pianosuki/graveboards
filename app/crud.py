import queue
from datetime import datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from .models import *
from .schemas import *

MIN_LIMIT = 1
MAX_LIMIT = 100
DEFAULT_LIMIT = 50


class CrudBase:
    def __init__(self, app: Flask | None = None):
        self.app = app

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        self.app = app
        app.extensions["crud"] = self

    @property
    def db(self) -> SQLAlchemy | None:
        return self.app.extensions.get("sqlalchemy")


class Crud(CrudBase):
    # Create #
    def add_user(self, user_id: int) -> User:
        user = User(id=user_id)

        self.db.session.add(user)
        self.db.session.commit()

        return user

    def add_mapper(self, user_dict: dict) -> Mapper:
        mapper = mapper_schema.load(user_dict)

        self.db.session.add(mapper)
        self.db.session.commit()

        return mapper

    def add_api_key(self, api_key: str, user_id: int) -> ApiKey:
        api_key = ApiKey(key=api_key, user_id=user_id)

        self.db.session.add(api_key)
        self.db.session.commit()

        return api_key

    def add_oauth_token(self, user_id: int, access_token: str, refresh_token: str, expires_at: int) -> OauthToken:
        oauth_token = OauthToken(user_id=user_id, access_token=access_token, refresh_token=refresh_token, expires_at=expires_at)

        self.db.session.add(oauth_token)
        self.db.session.commit()

        return oauth_token

    def add_score_fetcher_task(self, user_id: int) -> ScoreFetcherTask:
        score_fetcher_task = ScoreFetcherTask(user_id=user_id)

        self.db.session.add(score_fetcher_task)
        self.db.session.commit()

        return score_fetcher_task

    def add_mapper_info_fetcher_task(self, mapper_id: int) -> MapperInfoFetcherTask:
        mapper_info_fetcher_task = MapperInfoFetcherTask(mapper_id=mapper_id)

        self.db.session.add(mapper_info_fetcher_task)
        self.db.session.commit()

        return mapper_info_fetcher_task

    def add_beatmap(self, beatmap_id: int, beatmapset_id: int, mapper_id: int) -> Beatmap:
        beatmap = Beatmap(id=beatmap_id, beatmapset_id=beatmapset_id, mapper_id=mapper_id)

        self.db.session.add(beatmap)
        self.db.session.commit()

        return beatmap

    def add_beatmap_snapshot(self, beatmap_dict: dict) -> BeatmapSnapshot:
        beatmap_snapshot = beatmap_snapshot_schema.load(beatmap_dict)

        self.db.session.add(beatmap_snapshot)
        self.db.session.commit()

        return beatmap_snapshot

    def add_beatmapset(self, beatmapset_id: int, mapper_id: int) -> Beatmapset:
        beatmapset = Beatmapset(id=beatmapset_id, mapper_id=mapper_id)

        self.db.session.add(beatmapset)
        self.db.session.commit()

        return beatmapset

    def add_beatmapset_snapshot(self, beatmapset_dict: dict, beatmap_snapshots: list[BeatmapsetSnapshot]) -> BeatmapsetSnapshot:
        beatmapset_snapshot = beatmapset_snapshot_schema.load(beatmapset_dict)
        beatmapset_snapshot.beatmap_snapshots.extend(beatmap_snapshots)

        self.db.session.add(beatmapset_snapshot)
        self.db.session.commit()

        return beatmapset_snapshot

    def add_beatmapset_listing(self, beatmapset_id: int, beatmapset_snapshot_id: int):
        beatmapset_listing = BeatmapsetListing(beatmapset_id=beatmapset_id, beatmapset_snapshot_id=beatmapset_snapshot_id)

        self.db.session.add(beatmapset_listing)
        self.db.session.commit()

        return beatmapset_listing

    def add_leaderboard(self, beatmap_id: int, beatmap_snapshot_id: int) -> Leaderboard:
        leaderboard = Leaderboard(beatmap_id=beatmap_id, beatmap_snapshot_id=beatmap_snapshot_id)

        self.db.session.add(leaderboard)
        self.db.session.commit()

        return leaderboard

    def add_score(self, score_dict: dict) -> Score:
        score = score_schema.load(score_dict)

        self.db.session.add(score)
        self.db.session.commit()

        return score

    def add_queue(self, user_id: int) -> Queue:
        queue = Queue(user_id=user_id)

        self.db.session.add(queue)
        self.db.session.commit()

        return queue

    def add_request(self, request_dict: dict) -> Request:
        request = request_schema.load(request_dict)

        self.db.session.add(request)
        self.db.session.commit()

        return request

    # Read #
    def get_user(self, **kwargs) -> User | None:
        return User.query.filter_by(**kwargs).one_or_none()

    def get_users(self, limit: int = DEFAULT_LIMIT, offset: int = 0, **kwargs) -> list[User]:
        return User.query.filter_by(**kwargs).limit(limit).offset(offset).all()

    def user_exists(self, user_id) -> bool:
        return User.query.filter_by(id=user_id).one_or_none() is not None

    def get_mapper(self, **kwargs) -> User | None:
        return Mapper.query.filter_by(**kwargs).one_or_none()

    def get_mappers(self, limit: int = DEFAULT_LIMIT, offset: int = 0, **kwargs) -> list[Mapper]:
        return Mapper.query.filter_by(**kwargs).limit(limit).offset(offset).all()

    def get_oauth_tokens(self, limit: int = DEFAULT_LIMIT, offset: int = 0, **kwargs) -> list[OauthToken]:
        return OauthToken.query.filter_by(**kwargs).limit(limit).offset(offset).all()

    def get_score_fetcher_task(self, **kwargs) -> ScoreFetcherTask | None:
        return ScoreFetcherTask.query.filter_by(**kwargs).one_or_none()

    def get_score_fetcher_tasks(self, limit: int = DEFAULT_LIMIT, offset: int = 0, **kwargs) -> list[ScoreFetcherTask]:
        return ScoreFetcherTask.query.filter_by(**kwargs).limit(limit).offset(offset).all()

    def get_mapper_info_fetcher_task(self, **kwargs) -> MapperInfoFetcherTask | None:
        return MapperInfoFetcherTask.query.filter_by(**kwargs).one_or_none()

    def get_mapper_info_fetcher_tasks(self, limit: int = DEFAULT_LIMIT, offset: int = 0, **kwargs) -> list[MapperInfoFetcherTask]:
        return MapperInfoFetcherTask.query.filter_by(**kwargs).limit(limit).offset(offset).all()

    def get_beatmap(self, **kwargs) -> Beatmap | None:
        return Beatmap.query.filter_by(**kwargs).one_or_none()

    def get_beatmaps(self, limit: int = DEFAULT_LIMIT, offset: int = 0, **kwargs) -> list[Beatmap]:
        return Beatmap.query.filter_by(**kwargs).limit(limit).offset(offset).all()

    def beatmap_exists(self, beatmap_id: int) -> bool:
        beatmap = Beatmap.query.get(beatmap_id)
        return beatmap is not None

    def get_beatmap_snapshot(self, **kwargs) -> BeatmapSnapshot | None:
        return BeatmapSnapshot.query.filter_by(**kwargs).one_or_none()

    def get_beatmap_snapshots(self, limit: int = DEFAULT_LIMIT, offset: int = 0, **kwargs) -> list[BeatmapSnapshot]:
        return BeatmapSnapshot.query.filter_by(**kwargs).limit(limit).offset(offset).all()

    def get_latest_beatmap_snapshot(self, beatmap_id: int) -> BeatmapSnapshot | None:
        return BeatmapSnapshot.query.filter_by(beatmap_id=beatmap_id).order_by(BeatmapSnapshot.id.desc()).first()

    def get_beatmapset(self, **kwargs) -> Beatmapset | None:
        return Beatmapset.query.filter_by(**kwargs).one_or_none()

    def get_beatmapsets(self, limit: int = DEFAULT_LIMIT, offset: int = 0, **kwargs) -> list[Beatmapset]:
        return Beatmapset.query.filter_by(**kwargs).limit(limit).offset(offset).all()

    def get_beatmapset_snapshot(self, **kwargs) -> BeatmapsetSnapshot | None:
        return BeatmapsetSnapshot.query.filter_by(**kwargs).one_or_none()

    def get_beatmapset_snapshots(self, limit: int = DEFAULT_LIMIT, offset: int = 0, **kwargs) -> list[BeatmapsetSnapshot]:
        return BeatmapsetSnapshot.query.filter_by(**kwargs).limit(limit).offset(offset).all()

    def get_latest_beatmapset_snapshot(self, beatmapset_id: int) -> BeatmapsetSnapshot | None:
        return BeatmapsetSnapshot.query.filter_by(beatmapset_id=beatmapset_id).order_by(BeatmapsetSnapshot.id.desc()).first()

    def get_beatmapset_listing(self, **kwargs) -> BeatmapsetListing | None:
        return BeatmapsetListing.query.filter_by(**kwargs).one_or_none()

    def get_beatmapset_listings(self, limit: int = DEFAULT_LIMIT, offset: int = 0, **kwargs) -> list[BeatmapsetListing]:
        return BeatmapsetListing.query.filter_by(**kwargs).limit(limit).offset(offset).all()

    def get_leaderboard(self, **kwargs) -> Leaderboard | None:
        return Leaderboard.query.filter_by(**kwargs).one_or_none()

    def get_leaderboards(self, limit: int = DEFAULT_LIMIT, offset: int = 0, **kwargs) -> list[Leaderboard]:
        return Leaderboard.query.filter_by(**kwargs).limit(limit).offset(offset).all()

    def score_is_unique(self, beatmap_id: int, created_at: datetime) -> bool:
        return Score.query.filter_by(beatmap_id=beatmap_id, created_at=created_at).one_or_none() is None

    def get_score(self, **kwargs) -> Score | None:
        return Score.query.filter_by(**kwargs).one_or_none()

    def get_scores(self, limit: int = DEFAULT_LIMIT, offset: int = 0, **kwargs) -> list[Score]:
        return Score.query.filter_by(**kwargs).limit(limit).offset(offset).all()

    def get_queue(self, **kwargs) -> Queue | None:
        return Queue.query.filter_by(**kwargs).one_or_none()

    def get_queues(self, limit: int = DEFAULT_LIMIT, offset: int = 0, **kwargs) -> list[Queue]:
        return Queue.query.filter_by(**kwargs).limit(limit).offset(offset).all()

    def get_request(self, **kwargs) -> Request | None:
        return Request.query.filter_by(**kwargs).one_or_none()

    def get_requests(self, limit: int = DEFAULT_LIMIT, offset: int = 0, **kwargs) -> list[Request]:
        return Request.query.filter_by(**kwargs).limit(limit).offset(offset).all()

    # Update #
    def update_mapper(self, mapper_id: int, **kwargs):
        mapper = Mapper.query.get(mapper_id)
        mapper_ = mapper_schema.load(kwargs)

        if mapper is None:
            raise ValueError(f"There is no mapper with the ID '{mapper_id}'")

        excluded_columns = ["id"]

        for column in mapper_.__table__.columns:
            if column.name in mapper.__table__.columns and column.name not in excluded_columns and column.name in kwargs:
                value = getattr(mapper_, column.name)
                setattr(mapper, column.name, value)

        self.db.session.merge(mapper)
        self.db.session.commit()

    def update_oauth_token(self, oauth_token_id: int, **kwargs):
        oauth_token = OauthToken.query.get(oauth_token_id)
        oauth_token_ = oauth_token_schema.load(kwargs)

        if oauth_token is None:
            raise ValueError(f"There is no oauth token with the ID '{oauth_token_id}'")

        excluded_columns = ["id", "user_id"]

        for column in oauth_token_.__table__.columns:
            if column.name in oauth_token.__table__.columns and column.name not in excluded_columns and column.name in kwargs:
                value = getattr(oauth_token_, column.name)
                setattr(oauth_token, column.name, value)

        self.db.session.merge(oauth_token)
        self.db.session.commit()

    def update_score_fetcher_task(self, score_fetcher_task_id: int, **kwargs):
        score_fetcher_task = ScoreFetcherTask.query.get(score_fetcher_task_id)
        score_fetcher_task_ = score_fetcher_task_schema.load(kwargs)

        if score_fetcher_task is None:
            raise ValueError(f"There is no task with the ID '{score_fetcher_task_id}'")

        excluded_columns = ["id", "user_id"]

        for column in score_fetcher_task_.__table__.columns:
            if column.name in score_fetcher_task.__table__.columns and column.name not in excluded_columns and column.name in kwargs:
                value = getattr(score_fetcher_task_, column.name)
                setattr(score_fetcher_task, column.name, value)

        self.db.session.merge(score_fetcher_task)
        self.db.session.commit()

    def update_mapper_info_fetcher_task(self, mapper_info_fetcher_task_id: int, **kwargs):
        mapper_info_fetcher_task = MapperInfoFetcherTask.query.get(mapper_info_fetcher_task_id)
        mapper_info_fetcher_task_ = mapper_info_fetcher_task_schema.load(kwargs)

        if mapper_info_fetcher_task is None:
            raise ValueError(f"There is no task with the ID '{mapper_info_fetcher_task_id}'")

        excluded_columns = ["id", "user_id"]

        for column in mapper_info_fetcher_task_.__table__.columns:
            if column.name in mapper_info_fetcher_task.__table__.columns and column.name not in excluded_columns and column.name in kwargs:
                value = getattr(mapper_info_fetcher_task_, column.name)
                setattr(mapper_info_fetcher_task, column.name, value)

        self.db.session.merge(mapper_info_fetcher_task)
        self.db.session.commit()

    def update_beatmapset_listing(self, beatmapset_listing_id: int, **kwargs):
        beatmapset_listing = BeatmapsetListing.query.get(beatmapset_listing_id)
        beatmapset_listing_ = beatmapset_listing_schema.load(kwargs)

        if beatmapset_listing is None:
            raise ValueError(f"There is no beatmapset listing with the ID '{beatmapset_listing_id}'")

        excluded_columns = ["id", "beatmapset_id"]

        for column in beatmapset_listing_.__table__.columns:
            if column.name in beatmapset_listing.__table__.columns and column.name not in excluded_columns and column.name in kwargs:
                value = getattr(beatmapset_listing_, column.name)
                setattr(beatmapset_listing, column.name, value)

        self.db.session.merge(beatmapset_listing)
        self.db.session.commit()

    # Delete #
