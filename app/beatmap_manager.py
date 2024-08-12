import os
from io import BytesIO
from zipfile import ZipFile

import httpx

from app import db
from app.osu_api import OsuAPIClient
from app.database.schemas import BeatmapSnapshotSchema, BeatmapsetSnapshotSchema
from .utils import combine_checksums
from .config import INSTANCE_DIR

BEATMAPS_PATH = os.path.join(INSTANCE_DIR, "beatmaps")
BEATMAPSETS_PATH = os.path.join(INSTANCE_DIR, "beatmapsets")
BEATMAP_DOWNLOAD_BASEURL = "https://osu.ppy.sh/osu/"
BEATMAP_SNAPSHOT_FILE_PATH = os.path.join(BEATMAPS_PATH, "{beatmap_id}/{snapshot_number}.osu")


class BeatmapManager:
    def __init__(self):
        self.oac = OsuAPIClient()

    def archive(self, beatmapset_id: int) -> list[int]:
        beatmapset_dict = self.oac.get_beatmapset(beatmapset_id)
        checksum = combine_checksums([beatmap["checksum"] for beatmap in beatmapset_dict["beatmaps"]])

        self._ensure_populated(beatmapset_dict)

        if not db.get_beatmapset_snapshot(checksum=checksum):
            beatmap_ids = self._snapshot(beatmapset_dict)

            self._download(beatmap_ids)

            return beatmap_ids
        else:
            return []

    def _ensure_populated(self, beatmapset_dict: dict):
        beatmapset_id = beatmapset_dict["id"]
        mapper_id = beatmapset_dict["user_id"]

        # Beatmapset
        try:
            self._ensure_mapper_populated(mapper_id)
        except httpx.HTTPError:
            self._add_banned_mapper(mapper_id, user_dict=beatmapset_dict["user"])

        if not db.get_beatmapset(id=beatmapset_id):
            db.add_beatmapset(id=beatmapset_id, mapper_id=mapper_id)

        # Beatmap
        for beatmap_dict in beatmapset_dict["beatmaps"]:
            beatmap_id = beatmap_dict["id"]
            mapper_id = beatmap_dict["user_id"]

            try:
                self._ensure_mapper_populated(mapper_id)
            except httpx.HTTPError:
                self._add_banned_mapper(mapper_id)

            if not db.get_beatmap(id=beatmap_id):
                db.add_beatmap(id=beatmap_id, beatmapset_id=beatmapset_id, mapper_id=mapper_id)

    def _ensure_mapper_populated(self, mapper_id: int):
        if not db.get_mapper(id=mapper_id):
            from api import v1 as api

            api.mappers.post({"user_id": mapper_id})

    def _add_banned_mapper(self, mapper_id: int, user_dict: dict = None):
        db.add_mapper(id=mapper_id, is_restricted=True, **{
            "avatar_url": user_dict["avatar_url"] if user_dict else None,
            "username": user_dict["username"] if user_dict else None,
            "country_code": user_dict["country_code"] if user_dict else None
        } if user_dict else {})

    def _snapshot(self, beatmapset_dict: dict) -> list[int]:
        beatmap_snapshots = []

        # BeatmapSnapshot
        for beatmap_dict in beatmapset_dict["beatmaps"]:
            checksum = beatmap_dict["checksum"]

            if not db.get_beatmap_snapshot(checksum=checksum):

                with db.session_scope() as session:
                    beatmap_snapshot = BeatmapSnapshotSchema(session=session).load(beatmap_dict)
                    session.add(beatmap_snapshot)

                beatmap_snapshots.append(beatmap_snapshot)

        # BeatmapsetSnapshot
        with db.session_scope() as session:
            beatmapset_snapshot = BeatmapsetSnapshotSchema(session=session).load(beatmapset_dict)
            beatmapset_snapshot.beatmap_snapshots = beatmap_snapshots
            session.add(beatmapset_snapshot)

        return [beatmap_snapshot.beatmap_id for beatmap_snapshot in beatmap_snapshots]

    def _download(self, beatmap_ids: list[int]):
        for beatmap_id in beatmap_ids:
            url = os.path.join(BEATMAP_DOWNLOAD_BASEURL, str(beatmap_id))

            output_directory = os.path.join(BEATMAPS_PATH, str(beatmap_id))
            os.makedirs(output_directory, exist_ok=True)
            snapshot_number = db.get_beatmap_snapshot(beatmap_id=beatmap_id, _reversed=True).snapshot_number
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
            beatmapset_snapshot = db.get_beatmapset_snapshot(beatmapset_id=beatmapset_id, snapshot_number=snapshot_number)

            for beatmap_snapshot in beatmapset_snapshot.beatmap_snapshots:
                beatmap_path = self.get_path(beatmap_snapshot.beatmap_id, beatmap_snapshot.snapshot_number)
                zip_file.write(beatmap_path, f"{beatmap_snapshot.beatmap_id}.osu")

        zip_buffer.seek(0)

        return zip_buffer
