from __future__ import annotations

import httpx
import time
from enum import Enum
from typing import TYPE_CHECKING

from flask import Flask

if TYPE_CHECKING:
    from authlib.integrations.flask_client import OAuth

API_BASEURL = "https://osu.ppy.sh/api/v2"


class APIEndpoint(Enum):
    # Beatmaps
    BEATMAP_PACKS = API_BASEURL + "/beatmaps/packs"
    BEATMAP_LOOKUP = API_BASEURL + "/beatmaps/lookup"
    BEATMAP_USER_SCORE = API_BASEURL + "/beatmaps/{beatmap}/scores/users/{user}"
    BEATMAP_USER_SCORES = API_BASEURL + "/beatmaps/{beatmap}/scores/users/{user}/all"
    BEATMAP_SCORES = API_BASEURL + "/beatmaps/{beatmap}/scores"
    BEATMAPS = API_BASEURL + "/beatmaps"
    BEATMAP = API_BASEURL + "/beatmaps/{beatmap}"
    BEATMAP_ATTRIBUTES = API_BASEURL + "/beatmaps/{beatmap}/attributes"

    # Beatmapsets
    BEATMAPSET_LOOKUP = API_BASEURL + "/beatmapsets/lookup"
    BEATMAPSET = API_BASEURL + "/beatmapsets/{beatmapset}"

    # Users
    ME = API_BASEURL + "/me"
    SCORES = API_BASEURL + "/users/{user}/scores/{type}"

    def format(self, *args, **kwargs) -> str:
        return str.format(self.value, *args, **kwargs)


class ScoreType(Enum):
    BEST = "best"
    FIRSTS = "firsts"
    RECENT = "recent"


class Ruleset(Enum):
    FRUITS = "fruits"
    MANIA = "mania"
    OSU = "osu"
    TAIKO = "taiko"


class OsuAPIBase:
    def __init__(self, app: Flask | None):
        self.app = app

        self._token: dict | None = None
        self._client: httpx.Client | None = None

        if app is not None:
            self.init_app(app)

    def __enter__(self):
        self.client = httpx.Client()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()

    def init_app(self, app: Flask):
        self.app = app
        app.extensions["osu_api"] = self

    def refresh_token(self):
        self.token = self.oauth.osu_client.fetch_access_token()

    @staticmethod
    def get_user_auth_header(access_token: str) -> dict:
        return {"Authorization": f"Bearer {access_token}"}

    @staticmethod
    def format_query_parameters(query_parameters: dict) -> str:
        parameter_strings = [f"{key}={value}" for key, value in query_parameters.items()]
        return f"?{'&'.join(parameter_strings)}"

    @property
    def oauth(self) -> OAuth | None:
        return self.app.extensions.get("authlib.integrations.flask_client")

    @property
    def token(self) -> str:
        if self._token is None or self._token.get("expires_at") < time.time():
            self.refresh_token()
        return self._token.get("access_token")

    @token.setter
    def token(self, value: dict):
        self._token = value

    @property
    def client(self) -> httpx.Client:
        return self._client if self._client is not None and not self._client.is_closed else httpx.Client()

    @client.setter
    def client(self, value: httpx.Client):
        self._client = value

    @property
    def auth_headers(self) -> dict:
        return {"Authorization": f"Bearer {self.token}"}


class OsuAPIClient(OsuAPIBase):
    # Beatmaps #
    def get_beatmap(self, beatmap_id: int) -> dict:
        url = APIEndpoint.BEATMAP.format(beatmap=beatmap_id)

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            **self.auth_headers
        }

        response = self.client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_beatmapset(self, beatmapset_id: int) -> dict:
        url = APIEndpoint.BEATMAPSET.format(beatmapset=beatmapset_id)

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            **self.auth_headers
        }

        response = self.client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    # Users #
    def get_own_data(self, access_token: str) -> dict:
        url = APIEndpoint.ME.value

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            **self.get_user_auth_header(access_token)
        }

        response = self.client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_user_scores(self, user_id: int, score_type: ScoreType, legacy_only: int = 0, include_fails: int = 0, mode: Ruleset | None = None, limit: int | None = None, offset: int | None = None):
        url = APIEndpoint.SCORES.format(user=user_id, type=score_type.value)

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            **self.auth_headers
        }

        query_parameters = {
            "legacy_only": legacy_only,
            "include_fails": include_fails,
        }

        if mode is not None:
            query_parameters["mode"] = mode.value

        if limit is not None:
            query_parameters["limit"] = limit

        if offset is not None:
            query_parameters["offset"] = offset

        url += self.format_query_parameters(query_parameters)

        response = self.client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
