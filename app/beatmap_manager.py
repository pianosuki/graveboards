import os
import httpx

from flask import Flask

from .osu_api import OsuAPIClient
from .crud import Crud

BEATMAPS_PATH = os.path.abspath("instance/beatmaps")
BEATMAP_DOWNLOAD_BASEURL = "https://osu.ppy.sh/osu/"
BEATMAP_VERSION_FILE_PATH = os.path.join(BEATMAPS_PATH, "{beatmap_id}/{version_number}.osu")


class BeatmapManagerBase:
    def __init__(self, app: Flask | None = None):
        self.app = app
        os.makedirs(BEATMAPS_PATH, exist_ok=True)

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        self.app = app
        app.extensions["beatmap_manager"] = self

    @property
    def api(self) -> OsuAPIClient | None:
        return self.app.extensions.get("osu_api")

    @property
    def crud(self) -> Crud | None:
        return self.app.extensions.get("crud")


class BeatmapManager(BeatmapManagerBase):
    def download(self, beatmap_id: int):
        beatmap_dict = self.api.get_beatmap(beatmap_id)
        self.ensure_populated(beatmap_dict)

        if not self.crud.beatmap_version_exists(beatmap_dict["checksum"]):
            url = BEATMAP_DOWNLOAD_BASEURL + str(beatmap_id)
            output_directory = os.path.join(BEATMAPS_PATH, str(beatmap_id))
            os.makedirs(output_directory, exist_ok=True)
            version_number = len(self.crud.get_beatmap_versions(beatmap_id=beatmap_id)) + 1
            output_path = os.path.join(output_directory, f"{version_number}.osu")

            if not os.path.exists(output_path):
                with httpx.stream("GET", url) as response:
                    with open(output_path, 'wb') as f:
                        for chunk in response.iter_bytes():
                            f.write(chunk)

                self.crud.add_beatmap_version(beatmap_dict)
                print(f"Downloaded beatmap version: {beatmap_id}/{version_number}")

    def ensure_populated(self, beatmap_dict: dict):
        beatmap_id = beatmap_dict["id"]

        if not self.crud.beatmap_exists(beatmap_id):
            beatmapset_id = beatmap_dict["beatmapset_id"]

            if not self.crud.beatmapset_exists(beatmapset_id):
                beatmapset_dict = self.api.get_beatmapset(beatmapset_id)
                self.crud.add_beatmapset(beatmapset_dict)

            self.crud.add_beatmap(beatmap_id=beatmap_id, beatmapset_id=beatmapset_id)

    @staticmethod
    def get(beatmap_id: int, version_number: int) -> bytes:
        file_path = BEATMAP_VERSION_FILE_PATH.format(beatmap_id=beatmap_id, version_number=version_number)

        with open(file_path, "rb") as file:
            file_bytes = file.read()

        return file_bytes

    @staticmethod
    def get_path(beatmap_id: int, version_number: int) -> str:
        return BEATMAP_VERSION_FILE_PATH.format(beatmap_id=beatmap_id, version_number=version_number)
