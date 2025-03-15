import os
import asyncio
from io import BytesIO
from zipfile import ZipFile

import httpx
import aiofiles
from httpx import HTTPError
from sqlalchemy.exc import IntegrityError

from app.osu_api import OsuAPIClient
from .database import PostgresqlDB
from .database.models import Profile, Tag
from .database.schemas import BeatmapSnapshotSchema, BeatmapsetSnapshotSchema, ProfileSchema
from .redis import RedisClient, Namespace, LOCK_EXPIRY
from .utils import combine_checksums, aware_utcnow
from .exceptions import RestrictedUserError
from .logger import logger
from .config import INSTANCE_DIR

BEATMAPS_PATH = os.path.join(INSTANCE_DIR, "beatmaps")
BEATMAPSETS_PATH = os.path.join(INSTANCE_DIR, "beatmapsets")
BEATMAP_DOWNLOAD_BASEURL = "https://osu.ppy.sh/osu/"
BEATMAP_SNAPSHOT_FILE_PATH = os.path.join(BEATMAPS_PATH, "{beatmap_id}/{snapshot_number}.osu")


class BeatmapManager:
    def __init__(self, rc: RedisClient, db: PostgresqlDB):
        self.rc = rc
        self.db = db
        self.oac = OsuAPIClient(rc)

    async def archive(self, beatmapset_id: int, download: bool = True) -> list[int]:
        beatmapset_dict = await self.oac.get_beatmapset(beatmapset_id)
        checksum = combine_checksums([beatmap["checksum"] for beatmap in beatmapset_dict["beatmaps"]])

        await self._ensure_populated(beatmapset_dict)

        if not await self.db.get_beatmapset_snapshot(checksum=checksum):
            beatmap_ids = await self._snapshot(beatmapset_dict)

            if download:
                await self._download(beatmap_ids)

            return beatmap_ids
        else:
            return []

    async def _ensure_populated(self, beatmapset_dict: dict):
        beatmapset_id = beatmapset_dict["id"]
        user_id = beatmapset_dict["user_id"]

        # Beatmapset
        try:
            await self._ensure_user_populated(user_id)
        except RestrictedUserError:
            user_dict = beatmapset_dict["user"]

            if user_dict.get("is_deleted", False):
                user_dict["username"] = beatmapset_dict.get("creator")

            await self._populate_profile(user_id, restricted_user_dict=user_dict, is_restricted=True)

        if not await self.db.get_beatmapset(id=beatmapset_id):
            await self.db.add_beatmapset(id=beatmapset_id, user_id=user_id)

        # Beatmap
        for beatmap_dict in beatmapset_dict["beatmaps"]:
            beatmap_id = beatmap_dict["id"]
            user_id = beatmap_dict["user_id"]

            try:
                await self._ensure_user_populated(user_id)
            except RestrictedUserError:
                await self._populate_profile(user_id, is_restricted=True)

            if not await self.db.get_beatmap(id=beatmap_id):
                await self.db.add_beatmap(id=beatmap_id, beatmapset_id=beatmapset_id, user_id=user_id)

    async def _ensure_user_populated(self, user_id: int):
        if not await self.db.get_user(id=user_id):
            await self.db.add_user(id=user_id)

        try:
            await self._populate_profile(user_id)
        except HTTPError:
            raise RestrictedUserError(user_id)

    async def _populate_profile(self, user_id: int, restricted_user_dict: dict = None, is_restricted: bool = False) -> Profile | None:
        restricted_user_dict = restricted_user_dict if restricted_user_dict is not None else {}
        lock_hash_name = Namespace.LOCK.hash_name(Namespace.OSU_USER_PROFILE.hash_name(user_id))

        try:
            lock_acquired = await self.rc.set(lock_hash_name, "locked", ex=LOCK_EXPIRY, nx=True)

            if not lock_acquired:
                for _ in range(LOCK_EXPIRY):
                    await asyncio.sleep(1)

                    if (profile := await self.db.get_profile(user_id=user_id)) and not is_restricted:
                        return profile

            if (profile := await self.db.get_profile(user_id=user_id)) and not is_restricted:
                return profile

            if not is_restricted:
                user_dict = await self.oac.get_user(user_id)
                profile_dict = ProfileSchema.model_validate(user_dict).model_dump()
            else:
                profile_dict = {
                    "user_id": user_id,
                    "is_restricted": True,
                    "avatar_url": restricted_user_dict.get("avatar_url"),
                    "username": restricted_user_dict.get("username"),
                    "country_code": restricted_user_dict.get("country_code"),
                }

            try:
                profile = await self.db.add_profile(**profile_dict)
            except IntegrityError:
                profile_id = (await self.db.get_profile(user_id=user_id)).id
                profile = await self.db.update_profile(profile_id, **profile_dict)

            task_id = (await self.db.get_profile_fetcher_task(user_id=user_id)).id
            await self.db.update_profile_fetcher_task(task_id, last_fetch=aware_utcnow())
        finally:
            await self.rc.delete(lock_hash_name)

        return profile

    async def _snapshot(self, beatmapset_dict: dict) -> list[int]:
        beatmap_snapshots = []
        snapshotted_beatmap_ids = []

        # BeatmapSnapshot
        for beatmap_dict in beatmapset_dict["beatmaps"]:
            beatmap_snapshot = await self.db.get_beatmap_snapshot(checksum=beatmap_dict["checksum"])

            if not beatmap_snapshot:
                beatmap_snapshot_dict = BeatmapSnapshotSchema.model_validate(beatmap_dict).model_dump(
                    exclude={"beatmapset_snapshots", "leaderboard", "owner_profiles"}
                )
                beatmap_snapshot_dict["owner_profiles"] = await self._populate_owner_profiles(beatmap_dict["owners"])
                beatmap_snapshot = await self.db.add_beatmap_snapshot(**beatmap_snapshot_dict)
                snapshotted_beatmap_ids.append(beatmap_snapshot.beatmap_id)

            beatmap_snapshots.append(beatmap_snapshot)

        # BeatmapsetSnapshot
        beatmapset_snapshot_dict = BeatmapsetSnapshotSchema.model_validate(beatmapset_dict).model_dump(
            exclude={"beatmap_snapshots", "tags", "user_profile"}
        )
        beatmapset_snapshot_dict["beatmap_snapshots"] = beatmap_snapshots
        beatmapset_snapshot_dict["tags"] = await self._populate_tags(beatmapset_dict["tags"])
        await self.db.add_beatmapset_snapshot(**beatmapset_snapshot_dict)

        return snapshotted_beatmap_ids

    async def _populate_owner_profiles(self, owners: list[dict[str, int | str]]) -> list[Profile]:
        user_ids = [owner["id"] for owner in owners]
        profiles = []

        for user_id in user_ids:
            if not await self.db.get_user(id=user_id):
                await self.db.add_user(id=user_id)

            try:
                profile = await self._populate_profile(user_id)
            except HTTPError:
                profile = await self._populate_profile(user_id, is_restricted=True)

            profiles.append(profile)

        return profiles

    async def _populate_tags(self, tags_str: str) -> list[Tag]:
        tag_strs = set(tag.strip() for tag in tags_str.split(" ") if tag.strip())
        tags = []

        if not tags_str:
            return []

        for tag_str in tag_strs:
            tag = await self.db.get_tag(name=tag_str)

            if not tag:
                tag = await self.db.add_tag(name=tag_str)

            tags.append(tag)

        return tags

    async def _download(self, beatmap_ids: list[int]):
        async with httpx.AsyncClient() as client:
            for beatmap_id in beatmap_ids:
                url = os.path.join(BEATMAP_DOWNLOAD_BASEURL, str(beatmap_id))
                output_directory = os.path.join(BEATMAPS_PATH, str(beatmap_id))
                os.makedirs(output_directory, exist_ok=True)
                snapshot_number = (await self.db.get_beatmap_snapshot(beatmap_id=beatmap_id, _reversed=True)).snapshot_number
                output_path = os.path.join(output_directory, f"{snapshot_number}.osu")

                async with client.stream("GET", url) as response:
                    async with aiofiles.open(output_path, "wb") as f:
                        async for chunk in response.aiter_bytes():
                            await f.write(chunk)

    @staticmethod
    async def get(beatmap_id: int, snapshot_number: int) -> bytes:
        file_path = BEATMAP_SNAPSHOT_FILE_PATH.format(beatmap_id=beatmap_id, snapshot_number=snapshot_number)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"No .osu file found for beatmap {beatmap_id}, snapshot {snapshot_number}")

        async with aiofiles.open(file_path, "rb") as file:
            return await file.read()

    @staticmethod
    def get_path(beatmap_id: int, snapshot_number: int) -> str:
        file_path = BEATMAP_SNAPSHOT_FILE_PATH.format(beatmap_id=beatmap_id, snapshot_number=snapshot_number)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"No .osu file found for beatmap {beatmap_id}, snapshot {snapshot_number}")

        return file_path

    async def get_zip(self, beatmapset_id: int, snapshot_number: int) -> BytesIO:
        beatmapset_snapshot = await self.db.get_beatmapset_snapshot(
            beatmapset_id=beatmapset_id,
            snapshot_number=snapshot_number,
            _auto_eager_loads={"beatmap_snapshots"}
        )

        if not beatmapset_snapshot:
            raise ValueError(f"No snapshot found for beatmapset {beatmapset_id}, snapshot {snapshot_number}")

        beatmap_paths = []

        for beatmap_snapshot in beatmapset_snapshot.beatmap_snapshots:
            beatmap_path = self.get_path(beatmap_snapshot.beatmap_id, beatmap_snapshot.snapshot_number)

            if os.path.exists(beatmap_path):
                beatmap_paths.append((beatmap_path, f"{beatmap_snapshot.beatmap_id}.osu"))
            else:
                logger.warning(f"File {beatmap_path} does not exist and will be skipped.")

        return await asyncio.to_thread(self._create_zip, beatmap_paths)

    @staticmethod
    def _create_zip(beatmap_paths: list[tuple[str, str]]) -> BytesIO:
        zip_buffer = BytesIO()

        with ZipFile(zip_buffer, "w") as zip_file:
            for beatmap_path, filename in beatmap_paths:
                zip_file.write(beatmap_path, filename)

        zip_buffer.seek(0)
        return zip_buffer
