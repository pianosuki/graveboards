import time
from enum import Enum

import httpx

from .oauth import OAuth

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
    USER = API_BASEURL + "/users/{user}/{mode}"

    def format(self, *args, **kwargs) -> str:
        args = [arg if arg is not None else "" for arg in args]
        kwargs = {key: value if value is not None else "" for key, value in kwargs.items()}

        return str.format(self.value, *args, **kwargs).rstrip("/")


class ScoreType(Enum):
    BEST = "best"
    FIRSTS = "firsts"
    RECENT = "recent"


class Ruleset(Enum):
    FRUITS = "fruits"
    MANIA = "mania"
    OSU = "osu"
    TAIKO = "taiko"


class OsuAPIClientBase:
    def __init__(self):
        self._oauth = OAuth()
        self._token: dict | None = None
        self._client: httpx.Client | None = None

    def __enter__(self):
        self.client = httpx.Client()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()

    def refresh_token(self):
        self.token = self._oauth.fetch_token(grant_type="client_credentials", scope="public")

    @staticmethod
    def get_user_auth_header(access_token: str) -> dict:
        return {"Authorization": f"Bearer {access_token}"}

    @staticmethod
    def format_query_parameters(query_parameters: dict) -> str:
        parameter_strings = [f"{key}={value}" for key, value in query_parameters.items()]

        return f"?{'&'.join(parameter_strings)}"

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


class OsuAPIClient(OsuAPIClientBase):
    # BEATMAPS
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

    # USERS
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

    def get_user(self, user_id: int, mode: Ruleset | None = None) -> dict:
        url = APIEndpoint.USER.format(user=user_id, mode=mode)

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            **self.auth_headers
        }

        response = self.client.get(url, headers=headers)
        response.raise_for_status()

        return response.json()
