import os, httpx
from flask import Flask
from .osu_api import OsuAPIClient
from .crud import Crud

BEATMAPS_PATH = os.path.abspath("instance/beatmaps")
BEATMAP_DOWNLOAD_BASEURL = "https://osu.ppy.sh/osu/"


class BeatmapManager:
    def __init__(self, app: Flask | None = None):
        self.app = app
        os.makedirs(BEATMAPS_PATH, exist_ok=True)

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        self.app = app
        app.extensions["beatmap_manager"] = self

    def download(self, beatmap_id: int):
        self.ensure_populated(beatmap_id)
        url = BEATMAP_DOWNLOAD_BASEURL + str(beatmap_id)
        output_directory = os.path.join(BEATMAPS_PATH, str(beatmap_id))
        os.makedirs(output_directory, exist_ok=True)
        version_id = self.crud.get_latest_beatmap_version(beatmap_id).id
        output_path = os.path.join(output_directory, f"{version_id}.osu")
        if not os.path.exists(output_path):
            with httpx.stream("GET", url) as response:
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_bytes():
                        f.write(chunk)
            print(f"Downloaded beatmap version: {beatmap_id}/{version_id}")

    def ensure_populated(self, beatmap_id: int):
        with self.api:
            beatmap_dict = self.api.get_beatmap(beatmap_id)
            if not self.crud.beatmap_exists(beatmap_id):
                beatmapset_id = beatmap_dict["beatmapset_id"]
                if not self.crud.beatmapset_exists(beatmapset_id):
                    beatmapset_dict = self.api.get_beatmapset(beatmapset_id)
                    self.crud.add_beatmapset(beatmapset_dict)
                beatmapset = self.crud.get_beatmapset(beatmapset_id=beatmapset_id)
                self.crud.add_beatmap(beatmap_id=beatmap_id, beatmapset_id=beatmapset.id)
            if not self.crud.beatmap_version_exists(beatmap_dict["checksum"]):
                self.crud.add_beatmap_version(beatmap_dict)

    @property
    def api(self) -> OsuAPIClient | None:
        return self.app.extensions.get("osu_api")

    @property
    def crud(self) -> Crud | None:
        return self.app.extensions.get("crud")
