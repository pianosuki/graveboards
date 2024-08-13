from __future__ import annotations

import os
import httpx
from typing import TYPE_CHECKING
from io import BytesIO
from zipfile import ZipFile

from flask import Flask

from .utils import combine_checksums

if TYPE_CHECKING:
    from .osu_api import OsuAPIClient
    from .crud import Crud

BEATMAPS_PATH = os.path.abspath("instance/beatmaps")
BEATMAPSETS_PATH = os.path.abspath("instance/beatmapsets")
BEATMAP_DOWNLOAD_BASEURL = "https://osu.ppy.sh/osu/"
BEATMAP_SNAPSHOT_FILE_PATH = os.path.join(BEATMAPS_PATH, "{beatmap_id}/{snapshot_number}.osu")


class BeatmapManagerBase:
    def __init__(self, app: Flask | None = None):
        self.app = app
        os.makedirs(BEATMAPS_PATH, exist_ok=True)
        os.makedirs(BEATMAPSETS_PATH, exist_ok=True)

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        self.app = app
        app.extensions["beatmap_manager"] = self

    @property
    def osu_api(self) -> OsuAPIClient | None:
        return self.app.extensions.get("osu_api")

    @property
    def crud(self) -> Crud | None:
        return self.app.extensions.get("crud")


class BeatmapManager(BeatmapManagerBase):
    def archive(self, beatmapset_id: int) -> list[int]:
        beatmapset_dict = self.osu_api.get_beatmapset(beatmapset_id)
        checksum = combine_checksums([beatmap["checksum"] for beatmap in beatmapset_dict["beatmaps"]])

        self._ensure_populated(beatmapset_dict)

        if not self.crud.get_beatmapset_snapshot(checksum=checksum):
            beatmap_ids = self._snapshot(beatmapset_dict)
            self._download(beatmap_ids)

            return beatmap_ids
        else:
            return []

    def _ensure_populated(self, beatmapset_dict: dict):
        beatmapset_id = beatmapset_dict["id"]
        beatmapset_mapper_id = beatmapset_dict["user_id"]

        # Beatmapset
        try:
            self._ensure_mapper_populated(beatmapset_mapper_id)
        except httpx.HTTPError:
            self._add_banned_mapper(beatmapset_dict["user"])

        if not self.crud.get_beatmapset(id=beatmapset_id):
            self.crud.add_beatmapset(beatmapset_id, beatmapset_mapper_id)

        # Beatmap
        for beatmap_dict in beatmapset_dict["beatmaps"]:
            beatmap_id = beatmap_dict["id"]
            beatmap_mapper_id = beatmap_dict["user_id"]

            try:
                self._ensure_mapper_populated(beatmap_mapper_id)
            except httpx.HTTPError:
                self._add_banned_mapper({
                    "id": beatmap_mapper_id,
                    "avatar_url": None,
                    "username": None,
                    "country_code": None
                })

            if not self.crud.get_beatmap(id=beatmap_id):
                self.crud.add_beatmap(beatmap_id, beatmapset_id, beatmap_mapper_id)

    def _ensure_mapper_populated(self, mapper_id: int):
        if not self.crud.get_mapper(id=mapper_id):
            from api import v1 as api

            api.mappers.post({"user_id": mapper_id})

    def _add_banned_mapper(self, user_dict: dict):
        self.crud.add_mapper({
            "id": user_dict["id"],
            "avatar_url": user_dict["avatar_url"],
            "username": user_dict["username"],
            "country_code": user_dict["country_code"],
            "is_restricted": True
        })

    def _snapshot(self, beatmapset_dict: dict) -> list[int]:
        beatmap_snapshots = []

        # BeatmapSnapshot
        for beatmap_dict in beatmapset_dict["beatmaps"]:
            checksum = beatmap_dict["checksum"]

            if not self.crud.get_beatmap_snapshot(checksum=checksum):
                beatmap_snapshot = self.crud.add_beatmap_snapshot(beatmap_dict)
                beatmap_snapshots.append(beatmap_snapshot)

        # BeatmapsetSnapshot
        self.crud.add_beatmapset_snapshot(beatmapset_dict, beatmap_snapshots)

        return [beatmap_snapshot.beatmap_id for beatmap_snapshot in beatmap_snapshots]

    def _download(self, beatmap_ids: list[int]):
        for beatmap_id in beatmap_ids:
            url = os.path.join(BEATMAP_DOWNLOAD_BASEURL, str(beatmap_id))

            output_directory = os.path.join(BEATMAPS_PATH, str(beatmap_id))
            os.makedirs(output_directory, exist_ok=True)
            snapshot_number = self.crud.get_latest_beatmap_snapshot(beatmap_id).snapshot_number
            output_path = os.path.join(output_directory, f"{snapshot_number}.osu")

            with httpx.stream("GET", url) as response:
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_bytes():
                        f.write(chunk)

    @staticmethod
    def get(beatmap_id: int, snapshot_number: int) -> bytes:
        file_path = BEATMAP_SNAPSHOT_FILE_PATH.format(beatmap_id=beatmap_id, snapshot_number=snapshot_number)

        with open(file_path, "rb") as file:
            file_bytes = file.read()

        return file_bytes

    @staticmethod
    def get_path(beatmap_id: int, snapshot_number: int) -> str:
        return BEATMAP_SNAPSHOT_FILE_PATH.format(beatmap_id=beatmap_id, snapshot_number=snapshot_number)

    def get_zip(self, beatmapset_id: int, snapshot_number: int) -> BytesIO:
        zip_buffer = BytesIO()

        with ZipFile(zip_buffer, "w") as zip_file:
            beatmapset_snapshot = self.crud.get_beatmapset_snapshot(beatmapset_id=beatmapset_id, snapshot_number=snapshot_number)

            for beatmap_snapshot in beatmapset_snapshot.beatmap_snapshots:
                beatmap_path = self.get_path(beatmap_snapshot.beatmap_id, beatmap_snapshot.snapshot_number)
                zip_file.write(beatmap_path, f"{beatmap_snapshot.beatmap_id}.osu")

        zip_buffer.seek(0)

        return zip_buffer
