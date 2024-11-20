import os
from io import BytesIO
from zipfile import ZipFile

import httpx

from api import v1 as api
from app import db
from app.osu_api import OsuAPIClient
from app.database.schemas import BeatmapSnapshotSchema, BeatmapsetSnapshotSchema
from .utils import combine_checksums
from .exceptions import RestrictedUserError
from .config import INSTANCE_DIR, PRIMARY_ADMIN_USER_ID

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
        user_id = beatmapset_dict["user_id"]
        tags_str = beatmapset_dict["tags"]

        # Beatmapset
        try:
            self._ensure_user_populated(user_id)
        except RestrictedUserError:
            user_dict = beatmapset_dict["user"]

            if user_dict.get("is_deleted", False):
                user_dict["username"] = beatmapset_dict.get("creator")

            self._add_restricted_profile(user_id, user_dict)

        self._ensure_tags_populated(tags_str)

        if not db.get_beatmapset(id=beatmapset_id):
            db.add_beatmapset(id=beatmapset_id, user_id=user_id)

        # Beatmap
        for beatmap_dict in beatmapset_dict["beatmaps"]:
            beatmap_id = beatmap_dict["id"]
            user_id = beatmap_dict["user_id"]

            try:
                self._ensure_user_populated(user_id)
            except RestrictedUserError:
                self._add_restricted_profile(user_id)

            if not db.get_beatmap(id=beatmap_id):
                db.add_beatmap(id=beatmap_id, beatmapset_id=beatmapset_id, user_id=user_id)

    @staticmethod
    def _ensure_user_populated(user_id: int):
        if not db.get_user(id=user_id):
            api.users.post({"user_id": user_id}, user=PRIMARY_ADMIN_USER_ID)

        if not db.get_profile(user_id=user_id):
            raise RestrictedUserError(user_id)

    @staticmethod
    def _add_restricted_profile(user_id: int, user_dict: dict = None):
        db.add_profile(
            user_id=user_id,
            is_restricted=True,
            **{
                "avatar_url": user_dict.get("avatar_url"),
                "username": user_dict.get("username"),
                "country_code": user_dict.get("country_code")
            } if user_dict else {}
        )

    @staticmethod
    def _ensure_tags_populated(tags_str: str):
        if not tags_str.strip():
            return

        for tag_str in tags_str.strip().split(" "):
            if tag_str and not db.get_tag(name=tag_str):
                db.add_tag(name=tag_str)

    @staticmethod
    def _snapshot(beatmapset_dict: dict) -> list[int]:
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
            beatmapset_snapshot.tags = [db.get_tag(name=tag_str, session=session) for tag_str in beatmapset_dict["tags"].strip().split(" ")] if beatmapset_dict["tags"].strip() else []
            session.add(beatmapset_snapshot)

        return [beatmap_snapshot.beatmap_id for beatmap_snapshot in beatmap_snapshots]

    @staticmethod
    def _download(beatmap_ids: list[int]):
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
            with db.session_scope() as session:
                beatmapset_snapshot = db.get_beatmapset_snapshot(beatmapset_id=beatmapset_id, snapshot_number=snapshot_number, session=session)

                for beatmap_snapshot in beatmapset_snapshot.beatmap_snapshots:
                    beatmap_path = self.get_path(beatmap_snapshot.beatmap_id, beatmap_snapshot.snapshot_number)
                    zip_file.write(beatmap_path, f"{beatmap_snapshot.beatmap_id}.osu")

        zip_buffer.seek(0)

        return zip_buffer
