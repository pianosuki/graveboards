from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
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

    # Read #
    def get_latest_row_id(self) -> int:
        result = self.db.session.execute(text("SELECT last_insert_rowid()"))
        return result.scalar()

    def get_beatmaps(self) -> list[Beatmap]:
        return Beatmap.query.all()

    def get_beatmap(self, **kwargs) -> Beatmap | None:
        return Beatmap.query.filter_by(**kwargs).one_or_none()

    def get_beatmap_version(self, **kwargs) -> BeatmapVersion | None:
        return BeatmapVersion.query.filter_by(**kwargs).one_or_none()

    def get_beatmapset(self, **kwargs) -> Beatmapset | None:
        return Beatmapset.query.filter_by(**kwargs).one_or_none()

    def get_latest_beatmap_version(self, beatmap_id: int) -> BeatmapVersion | None:
        return BeatmapVersion.query.filter_by(beatmap_id=beatmap_id).order_by(BeatmapVersion.id.desc()).first()

    def beatmap_exists(self, beatmap_id: int) -> bool:
        beatmap = Beatmap.query.get(beatmap_id)
        return beatmap is not None

    def beatmap_version_exists(self, checksum: str) -> bool:
        beatmap_version = BeatmapVersion.query.filter_by(checksum=checksum).first()
        return beatmap_version is not None

    def beatmapset_exists(self, beatmapset_id: int) -> bool:
        beatmapset = Beatmapset.query.get(beatmapset_id)
        return beatmapset is not None

    # Update #

    # Delete #
