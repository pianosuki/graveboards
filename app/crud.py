from datetime import datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from .models import *
from .schemas import *


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
    def add_user(self, user_id: int):
        user = User(id=user_id)
        self.db.session.add(user)
        self.db.session.commit()

    def add_api_key(self, api_key: str, user_id: int):
        api_key = ApiKey(key=api_key, user_id=user_id)
        self.db.session.add(api_key)
        self.db.session.commit()

    def add_oauth_token(self, user_id: int, access_token: str, refresh_token: str, expires_at: int):
        oauth_token = OauthToken(user_id=user_id, access_token=access_token, refresh_token=refresh_token, expires_at=expires_at)
        self.db.session.add(oauth_token)
        self.db.session.commit()

    def add_score_fetcher_task(self, user_id):
        score_fetcher_task = ScoreFetcherTask(user_id=user_id)
        self.db.session.add(score_fetcher_task)
        self.db.session.commit()

    def add_beatmap(self, beatmap_id: int, beatmapset_id: int):
        beatmap = Beatmap(id=beatmap_id, beatmapset_id=beatmapset_id)
        self.db.session.add(beatmap)
        self.db.session.commit()

    def add_beatmap_version(self, beatmap_dict: dict):
        beatmap_version = beatmap_version_schema.load(beatmap_dict)
        self.db.session.add(beatmap_version)
        self.db.session.commit()

    def add_beatmapset(self, beatmapset_dict: dict):
        beatmapset = beatmapset_schema.load(beatmapset_dict)
        self.db.session.add(beatmapset)
        self.db.session.commit()

    def add_leaderboard(self, beatmap_id: int, beatmap_version_id: int):
        leaderboard = Leaderboard(beatmap_id=beatmap_id, beatmap_version_id=beatmap_version_id)
        self.db.session.add(leaderboard)
        self.db.session.commit()

    def add_score(self, score_dict: dict):
        score = score_schema.load(score_dict)
        self.db.session.add(score)
        self.db.session.commit()

    def add_request(self, request_dict: dict):
        request = request_schema.load(request_dict)
        self.db.session.add(request)
        self.db.session.commit()

    # Read #
    def user_exists(self, user_id) -> bool:
        return User.query.filter_by(id=user_id).one_or_none() is not None

    def get_oauth_tokens(self, **kwargs) -> list[OauthToken]:
        return OauthToken.query.filter_by(**kwargs).all()

    def get_score_fetcher_task(self, **kwargs) -> ScoreFetcherTask | None:
        return ScoreFetcherTask.query.filter_by(**kwargs).one_or_none()

    def get_score_fetcher_tasks(self, **kwargs) -> list[ScoreFetcherTask]:
        return ScoreFetcherTask.query.filter_by(**kwargs).all()

    def get_beatmap(self, **kwargs) -> Beatmap | None:
        return Beatmap.query.filter_by(**kwargs).one_or_none()

    def get_beatmaps(self, **kwargs) -> list[Beatmap]:
        return Beatmap.query.filter_by(**kwargs).all()

    def get_beatmap_version(self, **kwargs) -> BeatmapVersion | None:
        return BeatmapVersion.query.filter_by(**kwargs).one_or_none()

    def get_beatmap_versions(self, **kwargs) -> list[BeatmapVersion]:
        return BeatmapVersion.query.filter_by(**kwargs).all()

    def get_beatmapset(self, **kwargs) -> Beatmapset | None:
        return Beatmapset.query.filter_by(**kwargs).one_or_none()

    def get_beatmapsets(self, **kwargs) -> list[Beatmapset]:
        return Beatmapset.query.filter_by(**kwargs).all()

    def get_leaderboard(self, **kwargs) -> Leaderboard | None:
        return Leaderboard.query.filter_by(**kwargs).one_or_none()

    def get_leaderboards(self, **kwargs) -> list[Leaderboard]:
        return Leaderboard.query.filter_by(**kwargs).all()

    def score_unique(self, beatmap_id: int, created_at: datetime) -> bool:
        return Score.query.filter_by(beatmap_id=beatmap_id, created_at=created_at).one_or_none() is None

    def get_score(self, **kwargs) -> Score | None:
        return Score.query.filter_by(**kwargs).one_or_none()

    def get_scores(self, **kwargs) -> list[Score]:
        return Score.query.filter_by(**kwargs).all()

    def get_request(self, **kwargs) -> Request | None:
        return Request.query.filter_by(**kwargs).one_or_none()

    def get_requests(self, **kwargs) -> list[Request]:
        return Request.query.filter_by(**kwargs).all()

    def get_latest_beatmap_version(self, beatmap_id: int) -> BeatmapVersion | None:
        return BeatmapVersion.query.filter_by(beatmap_id=beatmap_id).order_by(BeatmapVersion.id.desc()).first()

    def beatmap_exists(self, beatmap_id: int) -> bool:
        beatmap = Beatmap.query.get(beatmap_id)
        return beatmap is not None

    def beatmapset_exists(self, beatmapset_id: int) -> bool:
        beatmapset = Beatmapset.query.get(beatmapset_id)
        return beatmapset is not None

    # Update #
    def update_oauth_token(self, oauth_token_id: int, **kwargs):
        oauth_token = OauthToken.query.get(oauth_token_id)

        if oauth_token is None:
            raise ValueError(f"There is no oauth token with the ID '{oauth_token_id}'")

        for key, value in kwargs.items():
            setattr(oauth_token, key, value)

        self.db.session.merge(oauth_token)
        self.db.session.commit()

    def update_score_fetcher_task(self, score_fetcher_task_id: int, **kwargs):
        score_fetcher_task = ScoreFetcherTask.query.get(score_fetcher_task_id)

        if score_fetcher_task is None:
            raise ValueError(f"There is no task with the ID '{score_fetcher_task_id}'")

        for key, value in kwargs.items():
            setattr(score_fetcher_task, key, value)

        self.db.session.merge(score_fetcher_task)
        self.db.session.commit()

    # Delete #
